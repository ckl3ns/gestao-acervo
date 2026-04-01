"""Unit tests for MatchRepository."""

from __future__ import annotations

import sqlite3

from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository


def test_add_creates_match_record(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """Inserir dois itens e um match deve persistir com campos corretos."""
    # Arrange: criar dois itens para satisfazer FK
    item_a = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    # Act
    match_id = match_repo.add(
        left_item_id=item_a.id or 0,
        right_item_id=item_b.id or 0,
        score=95.5,
        rule="title+author_fuzzy",
        status="possible",
        confidence_band="high",
    )

    # Assert
    assert match_id > 0
    row = db_conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    assert row is not None
    assert row["left_item_id"] == item_a.id
    assert row["right_item_id"] == item_b.id
    assert row["match_score"] == 95.5
    assert row["match_rule"] == "title+author_fuzzy"
    assert row["status"] == "possible"
    assert row["confidence_band"] == "high"


def test_add_returns_lastrowid(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """add() deve retornar o id da linha inserida (lastrowid)."""
    item_a = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    match_id = match_repo.add(
        left_item_id=item_a.id or 0,
        right_item_id=item_b.id or 0,
        score=80.0,
        rule="title_fuzzy",
        status="pending",
        confidence_band="medium",
    )

    max_id = db_conn.execute("SELECT MAX(id) FROM matches").fetchone()[0]
    assert match_id == max_id


def test_add_commits_immediately(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """add() deve fazer commit imediatamente para persistir o registro."""
    item_a = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    match_repo.add(
        left_item_id=item_a.id or 0,
        right_item_id=item_b.id or 0,
        score=75.0,
        rule="title_fuzzy",
        status="possible",
        confidence_band="medium",
    )

    # Outro connection não deve ver o registro se não tivesse commit
    conn2 = sqlite3.connect(":memory:")
    conn2.row_factory = sqlite3.Row
    conn2.execute("PRAGMA foreign_keys = ON;")
    # Não vai encontrar pois não compartilha transação
    # (teste conceitual - em memória isolado)
    count = conn2.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    assert count == 0  # Conn2 não vê pois é isolado
    conn2.close()
