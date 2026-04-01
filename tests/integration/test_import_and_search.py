"""Testes de integração: fluxo básico import + search (trilha canônica)."""

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
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger


def test_import_and_search_flow(
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

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=Path("data/samples/mock_source.csv"))

    results = SearchCatalogUseCase(item_repo).execute("teologia")
    assert len(results) >= 1
    assert "teologia" in (results[0].title_norm or "")
