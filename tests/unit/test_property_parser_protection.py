"""Property-based test for parser failure protection.

# Feature: core-integrity-fixes, Property 3: parser failure never leaves job running
"""

from __future__ import annotations

import sqlite3
from contextlib import suppress
from pathlib import Path
from typing import Any

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
PARSER_NAME = "prop_parser_failure"


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


def _make_source(conn: sqlite3.Connection) -> int:
    cursor = conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("PropParserSource", "mock", PARSER_NAME),
    )
    conn.commit()
    return int(cursor.lastrowid)


class _PropertyParser(BaseParser):
    parser_name = PARSER_NAME

    def __init__(self, fail: bool) -> None:
        self._fail = fail

    def parse(self, file_path: Path) -> list[dict[str, Any]]:
        if self._fail:
            raise RuntimeError("Parser explodiu")
        return [{"source_key": "prop3-item-001", "title": "Título OK", "item_type": "book"}]


@settings(max_examples=100)
@given(st.booleans())
def test_property_no_job_remains_running_after_execute(parser_fails: bool) -> None:
    """For any parser outcome, no import job must remain in status='running'."""
    conn = _make_conn()
    try:
        source_id = _make_source(conn)
        parser = _PropertyParser(fail=parser_fails)
        registry = ParserRegistry([parser])

        use_case = ImportSourceItemsFromSourceUseCase(
            source_lookup=SourceLookupRepository(conn),
            alias_lookup=AliasRepository(conn),
            parser_registry=registry,
            import_repository=ImportRepository(conn),
            item_repository=CatalogItemRepository(conn),
            logger=ProcessingLogger(conn),
        )

        with suppress(RuntimeError):
            use_case.execute(source_id, Path("dummy.csv"))

        row = conn.execute(
            "SELECT status FROM imports ORDER BY id DESC LIMIT 1"
        ).fetchone()

        assert row is not None
        assert row["status"] != "running"
    finally:
        conn.close()
