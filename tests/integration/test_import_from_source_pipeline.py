from pathlib import Path

from catalogo_acervo.application.use_cases.import_source_items_from_source import ImportSourceItemsFromSourceUseCase
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import CatalogItemRepository
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_lookup_repository import SourceLookupRepository
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger


def test_import_pipeline_resolves_parser_and_aliases(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = get_connection(db_path)
    schema_path = Path("src/catalogo_acervo/infrastructure/db/schema.sql")
    init_db(conn, schema_path)

    source_repo = SourceRepository(conn)
    source_lookup = SourceLookupRepository(conn)
    alias_repo = AliasRepository(conn)
    item_repo = CatalogItemRepository(conn)
    import_repo = ImportRepository(conn)
    logger = ProcessingLogger(conn)
    registry = ParserRegistry([MockParser()])

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
        parser_registry=registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )
    import_uc.execute(source_id=source_id, file_path=Path("data/samples/mock_source.csv"))

    results = SearchCatalogUseCase(item_repo).execute('author_norm:"equipe do seminario"')
    assert len(results) == 1
    assert results[0].author_norm == "equipe do seminario"
