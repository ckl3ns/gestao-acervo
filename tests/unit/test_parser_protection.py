"""Testes unitários para proteção do parser no pipeline de importação.

Validates: Requirements 4.1, 4.2, 4.4, 4.5
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

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
from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

_DUMMY_FILE = Path("dummy.csv")


class _FailingParser(BaseParser):
    parser_name = "failing_parser"

    def parse(self, file_path: Path) -> list[dict]:
        raise RuntimeError("Parser explodiu")


class _SuccessParser(BaseParser):
    parser_name = "success_parser"

    def parse(self, file_path: Path) -> list[dict]:
        return [
            {
                "source_key": "item-001",
                "title": "Livro de Teste",
                "item_type": "book",
            }
        ]


def _make_use_case(
    db_conn: sqlite3.Connection,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
    parser: BaseParser,
) -> ImportSourceItemsFromSourceUseCase:
    registry = ParserRegistry([parser])
    return ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
    )


def test_parser_failure_sets_failed_status(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
) -> None:
    """Validates: Requirements 4.1, 4.2 — falha no parser grava status='failed' no banco."""
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Fonte Falha",
        source_type="csv",
        parser_name=_FailingParser.parser_name,
    )
    use_case = _make_use_case(
        db_conn, source_lookup, alias_repo, item_repo, import_repo, logger, _FailingParser()
    )

    try:
        use_case.execute(source_id, _DUMMY_FILE)
    except RuntimeError:
        pass

    row = db_conn.execute(
        "SELECT status, total_errors FROM imports ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row["status"] == "failed"
    assert row["total_errors"] == 1


def test_parser_failure_reraises(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
) -> None:
    """Validates: Requirements 4.4, 4.5 — exceção do parser é re-lançada após finish()."""
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Fonte Falha Reraise",
        source_type="csv",
        parser_name=_FailingParser.parser_name,
    )
    use_case = _make_use_case(
        db_conn, source_lookup, alias_repo, item_repo, import_repo, logger, _FailingParser()
    )

    with pytest.raises(RuntimeError, match="Parser explodiu"):
        use_case.execute(source_id, _DUMMY_FILE)


def test_no_job_stays_running_on_success(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    logger: ProcessingLogger,
) -> None:
    """Validates: Requirements 4.1 — importação bem-sucedida não deixa status='running'."""
    source_id = RegisterSourceUseCase(source_repo).execute(
        name="Fonte Sucesso",
        source_type="csv",
        parser_name=_SuccessParser.parser_name,
    )
    use_case = _make_use_case(
        db_conn, source_lookup, alias_repo, item_repo, import_repo, logger, _SuccessParser()
    )

    use_case.execute(source_id, _DUMMY_FILE)

    row = db_conn.execute(
        "SELECT status FROM imports ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row["status"] != "running"
