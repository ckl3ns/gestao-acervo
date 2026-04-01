"""Property-based test for parser protection in the import pipeline.

# Feature: core-integrity-fixes, Property 3: no job stays running
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_lookup_repository import (
    SourceLookupRepository,
)
from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")

_FAILING_PARSER_NAME = "prop3_failing_parser"
_SUCCESS_PARSER_NAME = "prop3_success_parser"


class _FailingParser(BaseParser):
    """Parser that always raises RuntimeError."""

    parser_name = _FAILING_PARSER_NAME

    def parse(self, file_path: Path) -> list[dict]:  # type: ignore[override]
        raise RuntimeError("Parser explodiu intencionalmente")


class _SuccessParser(BaseParser):
    """Parser that returns one valid record."""

    parser_name = _SUCCESS_PARSER_NAME

    def parse(self, file_path: Path) -> list[dict]:  # type: ignore[override]
        return [
            {
                "source_key": "prop3-item-001",
                "title": "Livro de Propriedade 3",
                "item_type": "book",
            }
        ]


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


def _make_source(conn: sqlite3.Connection, parser_name: str) -> int:
    cursor = conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        (f"Prop3Source-{parser_name}", "mock", parser_name),
    )
    conn.commit()
    return int(cursor.lastrowid)


# ---------------------------------------------------------------------------
# Property 3: no job stays running
# Validates: Requirements 4.1, 4.2, 4.4, 4.5
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(st.booleans())
def test_property_no_job_stays_running(parser_fails: bool) -> None:
    """For any execution of the import pipeline — whether the parser fails or succeeds —
    the ImportJob must not remain with status='running' after execute() returns.

    Feature: core-integrity-fixes, Property 3: no job stays running
    Validates: Requirements 4.1, 4.2, 4.4, 4.5
    """
    conn = _make_conn()

    if parser_fails:
        parser: BaseParser = _FailingParser()
        source_id = _make_source(conn, _FAILING_PARSER_NAME)
    else:
        parser = _SuccessParser()
        source_id = _make_source(conn, _SUCCESS_PARSER_NAME)

    registry = ParserRegistry([parser])
    use_case = ImportSourceItemsFromSourceUseCase(
        source_lookup=SourceLookupRepository(conn),
        alias_lookup=AliasRepository(conn),
        parser_registry=registry,
        import_repository=ImportRepository(conn),
        item_repository=CatalogItemRepository(conn),
        logger=ProcessingLogger(conn),
    )

    try:
        use_case.execute(source_id, Path("dummy.csv"))
    except RuntimeError:
        # Expected when parser_fails=True; the job must still be finalized
        pass

    row = conn.execute(
        "SELECT status FROM imports ORDER BY id DESC LIMIT 1"
    ).fetchone()

    assert row is not None, "Expected an import job to exist in the DB"
    assert row["status"] != "running", (
        f"ImportJob must not remain 'running' after execute() "
        f"(parser_fails={parser_fails}), got status={row['status']!r}"
    )
