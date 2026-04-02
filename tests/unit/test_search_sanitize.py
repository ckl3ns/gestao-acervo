"""Testes unitários para sanitização de queries FTS5 — Requirement 6."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from catalogo_acervo.application.use_cases.search_catalog import (
    SearchCatalogUseCase,
    _sanitize_fts5_query,
)
from catalogo_acervo.infrastructure.db.bootstrap import init_db
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)

_SCHEMA_PATH = (
    __import__("pathlib").Path(__file__).parent.parent.parent
    / "src/catalogo_acervo/infrastructure/db/schema.sql"
)


@pytest.fixture()
def db_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn, _SCHEMA_PATH)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# _sanitize_fts5_query — testes unitários puros (sem banco)
# ---------------------------------------------------------------------------


def test_fts5_empty_query_returns_empty_string() -> None:
    assert _sanitize_fts5_query("") == ""


def test_fts5_whitespace_only_returns_empty_string() -> None:
    assert _sanitize_fts5_query("   ") == ""


def test_fts5_normal_query_is_quoted() -> None:
    result = _sanitize_fts5_query("teologia")
    assert result == '"teologia"'


def test_fts5_unbalanced_open_paren_removed() -> None:
    result = _sanitize_fts5_query("(foo")
    assert "(" not in result
    assert result != ""  # palavra preservada


def test_fts5_unbalanced_close_paren_removed() -> None:
    result = _sanitize_fts5_query("foo)")
    assert ")" not in result


def test_fts5_balanced_parens_words_preserved() -> None:
    result = _sanitize_fts5_query("(foo bar)")
    assert "(" not in result
    assert result == '"foo" "bar"'


def test_fts5_unclosed_quote_removed() -> None:
    result = _sanitize_fts5_query('"unterminated')
    assert result == '"unterminated"'


def test_fts5_closed_quotes_words_preserved() -> None:
    result = _sanitize_fts5_query('"frase exata"')
    assert result == '"frase" "exata"'


def test_fts5_isolated_and_operator_removed() -> None:
    result = _sanitize_fts5_query("AND")
    assert result == ""


def test_fts5_isolated_or_operator_removed() -> None:
    result = _sanitize_fts5_query("OR")
    assert result == ""


def test_fts5_isolated_not_operator_removed() -> None:
    result = _sanitize_fts5_query("NOT")
    assert result == ""


def test_fts5_hyphenated_token_is_quoted() -> None:
    result = _sanitize_fts5_query("0-0")
    assert result == '"0-0"'


def test_fts5_alpha_hyphen_token_is_quoted() -> None:
    result = _sanitize_fts5_query("abc-def")
    assert result == '"abc-def"'


def test_fts5_cj_date_style_query_no_error() -> None:
    result = _sanitize_fts5_query("C. J. Date")
    assert result == '"C" "J" "Date"'


# ---------------------------------------------------------------------------
# SearchCatalogUseCase.execute() — não deve lançar exceção com inputs ruins
# ---------------------------------------------------------------------------


def test_search_empty_query_returns_empty_list(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    assert uc.execute("") == []


def test_search_whitespace_query_returns_empty_list(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    assert uc.execute("   ") == []


def test_search_unbalanced_parens_no_exception(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    result = uc.execute("(foo")
    assert isinstance(result, list)


def test_search_unclosed_quote_no_exception(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    result = uc.execute('"unterminated')
    assert isinstance(result, list)


def test_search_hyphenated_numeric_token_no_exception(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    result = uc.execute("0-0")
    assert isinstance(result, list)


def test_search_isolated_operator_no_exception(db_conn: sqlite3.Connection) -> None:
    uc = SearchCatalogUseCase(CatalogItemRepository(db_conn))
    result = uc.execute("AND")
    assert isinstance(result, list)
