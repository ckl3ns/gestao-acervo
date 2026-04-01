"""Property-based test for FTS5 query sanitization safety.

# Feature: core-integrity-fixes, Property 8: FTS5 sanitization safety
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn, SCHEMA_PATH)
    return conn


@settings(max_examples=200)
@given(st.text())
def test_property_fts5_never_raises(query: str) -> None:
    """For any string input, SearchCatalogUseCase.execute() must never raise OperationalError.

    # Feature: core-integrity-fixes, Property 8: FTS5 sanitization safety
    Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
    """
    conn = _make_conn()
    uc = SearchCatalogUseCase(CatalogItemRepository(conn))

    try:
        result = uc.execute(query)
        assert isinstance(result, list)
    except sqlite3.OperationalError as exc:
        raise AssertionError(
            f"SearchCatalogUseCase.execute() raised OperationalError for query {query!r}: {exc}"
        ) from exc
