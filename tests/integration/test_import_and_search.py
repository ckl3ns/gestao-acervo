from pathlib import Path

from catalogo_acervo.application.use_cases.import_source_items import ImportSourceItemsUseCase
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import CatalogItemRepository
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger


def test_import_and_search_flow(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = get_connection(db_path)
    schema_path = Path("src/catalogo_acervo/infrastructure/db/schema.sql")
    init_db(conn, schema_path)

    source_repo = SourceRepository(conn)
    item_repo = CatalogItemRepository(conn)
    import_repo = ImportRepository(conn)
    logger = ProcessingLogger(conn)

    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Mock Source",
        source_type="mock",
        parser_name="mock_csv",
    )

    import_uc = ImportSourceItemsUseCase(MockParser(), import_repo, item_repo, logger)
    import_uc.execute(source_id=source_id, file_path=Path("data/samples/mock_source.csv"))

    results = SearchCatalogUseCase(item_repo).execute("teologia")
    assert len(results) >= 1
    assert "teologia" in (results[0].title_norm or "")
