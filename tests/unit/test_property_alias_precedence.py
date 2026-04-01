"""Property-based tests for alias scoped precedence.

# Feature: core-integrity-fixes, Property 7: alias scoped precedence
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from catalogo_acervo.domain.services.aliasing import apply_aliases
from catalogo_acervo.domain.services.normalization import normalize_text
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


@settings(max_examples=100)
@given(
    st.text(min_size=1),
    st.text(min_size=1),
    st.text(min_size=1),
)
def test_property_scoped_alias_wins_over_global(
    alias_text: str,
    global_canonical: str,
    scoped_canonical: str,
) -> None:
    """A scoped alias must take precedence over a global alias for the same alias_text."""
    assume(normalize_text(alias_text) is not None)
    assume(normalize_text(global_canonical) != normalize_text(scoped_canonical))
    assume(normalize_text(global_canonical) is not None)
    assume(normalize_text(scoped_canonical) is not None)

    conn = _make_conn()
    try:
        repo = AliasRepository(conn)
        repo.upsert(
            alias_kind="author",
            alias_text=alias_text,
            canonical_text=global_canonical,
            source_scope=None,
        )
        repo.upsert(
            alias_kind="author",
            alias_text=alias_text,
            canonical_text=scoped_canonical,
            source_scope="test_scope",
        )

        aliases = repo.list_active()
        result = apply_aliases(
            alias_text,
            alias_kind="author",
            aliases=aliases,
            source_scope="test_scope",
        )

        expected = normalize_text(scoped_canonical)
        assert result == expected, (
            f"Expected scoped canonical {expected!r} to win over global, but got {result!r}. "
            f"alias_text={alias_text!r}, global={normalize_text(global_canonical)!r}, "
            f"scoped={normalize_text(scoped_canonical)!r}"
        )
    finally:
        conn.close()
