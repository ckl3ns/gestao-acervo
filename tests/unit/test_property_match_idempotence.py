"""Property-based tests for match idempotence.

# Feature: core-integrity-fixes, Property 4: match idempotence
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


def _insert_source(conn: sqlite3.Connection, name: str) -> int:
    cursor = conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        (name, "mock", "mock_parser"),
    )
    conn.commit()
    return int(cursor.lastrowid)


@settings(max_examples=100)
@given(
    st.lists(
        st.text(min_size=1, alphabet=st.characters(whitelist_categories=("L",))),
        min_size=2,
        max_size=6,
    )
)
def test_property_match_idempotence(titles: list[str]) -> None:
    """Running SuggestMatchesUseCase.execute() twice must not change the match count."""
    conn = _make_conn()
    try:
        source_a_id = _insert_source(conn, "SourceA")
        source_b_id = _insert_source(conn, "SourceB")

        item_repo = CatalogItemRepository(conn)
        match_repo = MatchRepository(conn)

        mid = max(1, len(titles) // 2)
        titles_a = titles[:mid]
        titles_b = titles[mid:]

        for idx, title in enumerate(titles_a):
            item = CatalogItem(
                source_id=source_a_id,
                source_key=f"a-{idx}",
                title_raw=title,
                raw_record_json={"title": title, "source_key": f"a-{idx}"},
            )
            item_repo.upsert(item)

        for idx, title in enumerate(titles_b):
            item = CatalogItem(
                source_id=source_b_id,
                source_key=f"b-{idx}",
                title_raw=title,
                raw_record_json={"title": title, "source_key": f"b-{idx}"},
            )
            item_repo.upsert(item)

        use_case = SuggestMatchesUseCase(items_repo=item_repo, match_repo=match_repo)
        use_case.execute()
        count_after_first = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

        use_case.execute()
        count_after_second = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

        assert count_after_second == count_after_first
    finally:
        conn.close()
