"""Property-based tests for match deduplication.

# Feature: core-integrity-fixes, Property 5: match deduplication
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


def _insert_catalog_item(conn: sqlite3.Connection, source_id: int, idx: int) -> int:
    cursor = conn.execute(
        """
        INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source_id, f"key-{idx}", "book", f"Title {idx}", "{}"),
    )
    conn.commit()
    return int(cursor.lastrowid)


def _insert_source(conn: sqlite3.Connection) -> int:
    cursor = conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("DeduplicationTestSource", "mock", "mock_parser"),
    )
    conn.commit()
    return int(cursor.lastrowid)


# ---------------------------------------------------------------------------
# Property 5: match deduplication
# Validates: Requirements 2.1, 2.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=1000),
)
def test_property_match_deduplication(left_id: int, right_id: int) -> None:
    """Adding the same match pair twice must not create duplicate rows.

    # Feature: core-integrity-fixes, Property 5: match deduplication
    Validates: Requirements 2.1, 2.2
    """
    assume(left_id != right_id)

    conn = _make_conn()
    source_id = _insert_source(conn)

    item_left = _insert_catalog_item(conn, source_id, left_id)
    item_right = _insert_catalog_item(conn, source_id, right_id)

    match_repo = MatchRepository(conn)

    # Call add twice with the same pair — must not raise
    match_repo.add(item_left, item_right, score=0.9, rule="exact_title", status="pending", confidence_band="high")
    match_repo.add(item_left, item_right, score=0.9, rule="exact_title", status="pending", confidence_band="high")

    count = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE left_item_id = ? AND right_item_id = ?",
        (item_left, item_right),
    ).fetchone()[0]

    assert count == 1, (
        f"Expected exactly 1 match row for pair ({item_left}, {item_right}), got {count}"
    )
