"""Testes de integração: pipeline de importação com source + aliases."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository
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
    source_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
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

    results = SearchCatalogUseCase(item_repo).execute("equipe do seminario")
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
    """FTS5 deve refletir valor atualizado após upsert com conflito - sem duplicatas."""
    source_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
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

    import_uc.execute(source_id=source_id, file_path=SAMPLE_FILE)
    results_before = SearchCatalogUseCase(item_repo).execute("teologia")
    assert len(results_before) >= 1

    import_uc.execute(source_id=source_id, file_path=SAMPLE_FILE)
    results_after = SearchCatalogUseCase(item_repo).execute("teologia")

    assert len(results_after) == len(results_before)


class _InvalidTitleParser(BaseParser):
    """Parser que retorna registros com título vazio para testar error path."""

    parser_name = "invalid_title"

    def parse(self, file_path: Path) -> list[dict[str, str | None]]:
        return [
            {
                "source_key": "BK-INVALID",
                "title": "",
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


class _MirrorParser(BaseParser):
    """Parser com um único registro parametrizável para testar matching canônico."""

    def __init__(self, parser_name: str, source_key: str) -> None:
        self.parser_name = parser_name
        self.source_key = source_key

    def parse(self, file_path: Path) -> list[dict[str, str]]:
        return [
            {
                "source_key": self.source_key,
                "title": "Introdução à Teologia",
                "author": "João Silva",
                "item_type": "book",
            }
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
    """Erro em registro individual não deve abortar importação inteira."""
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

    row = db_conn.execute(
        "SELECT status, total_read, total_inserted, total_updated, total_skipped, total_errors FROM imports ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row is not None
    status, _total_read, total_inserted, total_updated, total_skipped, total_errors = row
    assert status == "completed_with_errors"
    assert total_errors == 1
    assert total_inserted == 1
    assert total_updated == 0
    assert total_skipped == 0

    results = SearchCatalogUseCase(item_repo).execute("Título Válido")
    assert len(results) == 1


def test_import_triggers_match_suggestions_without_symmetric_duplicates(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    match_repo: MatchRepository,
    logger: ProcessingLogger,
) -> None:
    """Após importar duas fontes equivalentes, deve existir um único match canônico."""
    parser_registry = ParserRegistry([
        _MirrorParser("mirror_a", "A-1"),
        _MirrorParser("mirror_b", "B-1"),
    ])

    source_a_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Source A",
        source_type="mock",
        parser_name="mirror_a",
    )
    source_b_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Source B",
        source_type="mock",
        parser_name="mirror_b",
    )

    suggest_uc = SuggestMatchesUseCase(items_repo=item_repo, match_repo=match_repo)
    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
        suggest_matches_use_case=suggest_uc,
    )

    import_uc.execute(source_id=source_a_id, file_path=SAMPLE_FILE)
    import_uc.execute(source_id=source_b_id, file_path=SAMPLE_FILE)

    matches = db_conn.execute(
        "SELECT left_item_id, right_item_id FROM matches ORDER BY id"
    ).fetchall()
    assert len(matches) == 1
    assert matches[0]["left_item_id"] < matches[0]["right_item_id"]


def test_register_source_rejects_unknown_parser(
    source_repo: SourceRepository,
    parser_registry: ParserRegistry,
) -> None:
    with pytest.raises(ValueError, match="não registrado"):
        RegisterSourceUseCase(source_repo, parser_registry).execute(
            name="Fonte Inválida",
            source_type="mock",
            parser_name="parser_ausente",
        )
