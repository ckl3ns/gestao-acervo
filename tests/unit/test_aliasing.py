import sqlite3
from pathlib import Path

import pytest

from catalogo_acervo.domain.entities.alias import Alias
from catalogo_acervo.domain.services.aliasing import apply_aliases
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


def test_apply_aliases_returns_canonical_text() -> None:
    aliases = [
        Alias(alias_kind="author", alias_text="wj grudem", canonical_text="wayne grudem", source_scope="mock_csv")
    ]

    normalized = apply_aliases(
        "wj grudem",
        alias_kind="author",
        aliases=aliases,
        source_scope="mock_csv",
    )

    assert normalized == "wayne grudem"


def test_apply_aliases_respects_source_scope() -> None:
    aliases = [
        Alias(alias_kind="author", alias_text="wj grudem", canonical_text="wayne grudem", source_scope="logos_csv")
    ]

    normalized = apply_aliases(
        "wj grudem",
        alias_kind="author",
        aliases=aliases,
        source_scope="mock_csv",
    )

    assert normalized == "wj grudem"


# --- Testes de precedência de aliases (Requirements 5.1–5.5) ---


def test_alias_scoped_wins_over_global(alias_repo: AliasRepository) -> None:
    """Alias específico de fonte deve ter precedência sobre alias global."""
    alias_repo.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="global canonical",
        source_scope=None,
    )
    alias_repo.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="scoped canonical",
        source_scope="mock_csv",
    )

    aliases = alias_repo.list_active()
    result = apply_aliases("j silva", alias_kind="author", aliases=aliases, source_scope="mock_csv")

    assert result == "scoped canonical"


def test_alias_global_used_when_no_scoped(alias_repo: AliasRepository) -> None:
    """Alias global deve ser aplicado quando não há alias específico para a fonte."""
    alias_repo.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="global canonical",
        source_scope=None,
    )

    aliases = alias_repo.list_active()
    result = apply_aliases("j silva", alias_kind="author", aliases=aliases, source_scope="mock_csv")

    assert result == "global canonical"


def test_alias_order_independent(db_conn: sqlite3.Connection) -> None:
    """Alias específico vence independente da ordem de inserção."""
    # Caso 1: scoped inserido primeiro, depois global
    repo1 = AliasRepository(db_conn)
    repo1.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="scoped canonical",
        source_scope="mock_csv",
    )
    repo1.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="global canonical",
        source_scope=None,
    )

    aliases = repo1.list_active()
    result = apply_aliases("j silva", alias_kind="author", aliases=aliases, source_scope="mock_csv")
    assert result == "scoped canonical"

    # Caso 2: nova conexão, global inserido primeiro, depois scoped
    conn2 = sqlite3.connect(":memory:")
    conn2.row_factory = sqlite3.Row
    conn2.execute("PRAGMA foreign_keys = ON;")
    init_db(conn2, SCHEMA_PATH)

    repo2 = AliasRepository(conn2)
    repo2.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="global canonical",
        source_scope=None,
    )
    repo2.upsert(
        alias_kind="author",
        alias_text="j silva",
        canonical_text="scoped canonical",
        source_scope="mock_csv",
    )

    aliases2 = repo2.list_active()
    result2 = apply_aliases("j silva", alias_kind="author", aliases=aliases2, source_scope="mock_csv")
    assert result2 == "scoped canonical"
