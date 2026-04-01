"""Testes de integração: pipeline de importação com source + aliases."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_lookup_repository import (
    SourceLookupRepository,
)
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

SAMPLE_FILE = Path("data/samples/mock_source.csv")


def test_import_pipeline_resolves_parser_and_aliases(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
    parser_registry: ParserRegistry,
) -> None:
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Mock Source",
        source_type="mock",
        parser_name="mock_csv",
    )
    alias_repo.upsert(
        alias_kind="author",
        alias_text="equipe seminario",
        canonical_text="equipe do seminario",
        source_scope="mock_csv",
    )

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=SAMPLE_FILE)

    results = SearchCatalogUseCase(item_repo).execute('author_norm:"equipe do seminario"')
    assert len(results) == 1
    assert results[0].author_norm == "equipe do seminario"


def test_fts5_stays_in_sync_after_upsert_conflict(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
    parser_registry: ParserRegistry,
) -> None:
    """FTS5 deve refletir valor atualizado após upsert com conflito — sem duplicatas."""
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="FTS Source",
        source_type="mock",
        parser_name="mock_csv",
    )
    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )

    # Primeira importação
    import_uc.execute(source_id=source_id, file_path=SAMPLE_FILE)
    results_before = SearchCatalogUseCase(item_repo).execute("teologia")
    assert len(results_before) >= 1, "Deve encontrar item após primeira importação"

    # Segunda importação (upsert com conflito — mesma source_key)
    import_uc.execute(source_id=source_id, file_path=SAMPLE_FILE)
    results_after = SearchCatalogUseCase(item_repo).execute("teologia")

    # FTS5 não deve acumular duplicatas nem perder o registro
    assert len(results_after) == len(results_before), (
        f"FTS5 dessincronizado: antes={len(results_before)}, depois={len(results_after)}"
    )


class _InvalidTitleParser(BaseParser):
    """Parser que retorna registros com título vazio para testar error path."""

    parser_name = "invalid_title"

    def parse(self, file_path: Path) -> list[dict]:
        return [
            {
                "source_key": "BK-INVALID",
                "title": "",  # ← gatilho para ValueError na linha 90-91
                "author": "Autor Teste",
                "series": None,
                "publisher": None,
                "year": "2020",
                "language": "pt",
                "item_type": "book",
                "resource_type": "pdf",
            },
            {
                "source_key": "BK-VALID",
                "title": "Título Válido",
                "author": "Autor Teste",
                "series": None,
                "publisher": None,
                "year": "2021",
                "language": "pt",
                "item_type": "book",
                "resource_type": "pdf",
            },
        ]


def test_import_handles_record_errors_gracefully(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
    parser_registry: ParserRegistry,
) -> None:
    """Erro em registro individual não deve abortar importação inteira.

    O primeiro registro tem título vazio e dispara ValueError no use case.
    O segundo registro é válido e deve ser importado normalmente.
    O job termina com status 'completed_with_errors' e erro é logado.
    """
    # Registrar fonte com parser que produz registros inválidos
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Invalid Source",
        source_type="mock",
        parser_name="invalid_title",
    )
    parser_registry.register(_InvalidTitleParser())

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=Path("data/samples/mock_source.csv"))

    # Job deve ter terminado com erro (1 erro, 1 inserção)
    row = db_conn.execute(
        "SELECT status, total_read, total_inserted, total_errors FROM imports ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row is not None
    status, _total_read, total_inserted, total_errors = row
    assert status == "completed_with_errors", f"Esperado 'completed_with_errors', got '{status}'"
    assert total_errors == 1, f"Esperado 1 erro, got {total_errors}"
    assert total_inserted == 1, f"Esperado 1 inserção, got {total_inserted}"

    # Item válido foi importado
    results = SearchCatalogUseCase(item_repo).execute("Título Válido")
    assert len(results) == 1
