from __future__ import annotations

import sqlite3
from pathlib import Path

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
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
from catalogo_acervo.infrastructure.ingestion.parsers.logos_csv_parser import (
    LogosCsvParser,
)
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

_LOGOS10_SAMPLE = Path("data/samples/logos10_sample.csv")
_LOGOS7_SAMPLE = Path("data/samples/logos7_sample.csv")


def test_import_pipeline_accepts_real_logos10_export_shape(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
) -> None:
    parser_registry = ParserRegistry([LogosCsvParser()])
    source_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Logos 10",
        source_type="biblioteca_digital",
        parser_name="logos_csv",
    )

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=_LOGOS10_SAMPLE)

    item = item_repo.get_by_source_and_key(source_id, "LLS:FDNMRTLDDDLM")
    assert item is not None
    assert item.title_raw == "Fedão (a imortalidade da alma)"
    assert item.author_raw == "Platão"
    assert item.publisher_raw == "Faithlife"
    assert item.year == 2021
    assert item.resource_type == "Monografia"


def test_import_pipeline_accepts_real_logos7_export_shape_without_publishers(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
) -> None:
    parser_registry = ParserRegistry([LogosCsvParser()])
    source_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Logos 7",
        source_type="biblioteca_digital",
        parser_name="logos_csv",
    )

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=_LOGOS7_SAMPLE)

    item = item_repo.get_by_source_and_key(source_id, "LLS:NIDOTTE")
    assert item is not None
    assert item.title_raw == "New International Dictionary of Old Testament Theology and Exegesis"
    assert item.author_raw == "VanGemeren, Willem A."
    assert item.publisher_raw is None
    assert item.year == 1997
    assert item.resource_type == "Léxico"
