"""Unit tests for MatchRepository."""

from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
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
        source_key="BK-MATCH-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-MATCH-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    # Buscar itens para obter IDs gerados pelo banco
    saved_a = item_repo.get_by_source_and_key(registered_source_id, "BK-MATCH-A")
    saved_b = item_repo.get_by_source_and_key(registered_source_id, "BK-MATCH-B")

    # Act
    match_id = match_repo.add(
        left_item_id=saved_a.id or 0,
        right_item_id=saved_b.id or 0,
        score=95.5,
        rule="title+author_fuzzy",
        status="possible",
        confidence_band="high",
    )

    # Assert
    assert match_id > 0
    row = db_conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    assert row is not None
    assert row["left_item_id"] == saved_a.id
    assert row["right_item_id"] == saved_b.id
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
        source_key="BK-ROWID-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-ROWID-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    saved_a = item_repo.get_by_source_and_key(registered_source_id, "BK-ROWID-A")
    saved_b = item_repo.get_by_source_and_key(registered_source_id, "BK-ROWID-B")

    match_id = match_repo.add(
        left_item_id=saved_a.id or 0,
        right_item_id=saved_b.id or 0,
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
    """add() deve fazer commit imediatamente — registro fica visível após add()."""
    item_a = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-COMMIT-A",
        item_type="book",
        title_raw="Título A",
        title_norm="titulo a",
        raw_record_json={},
        current_import_id=None,
    )
    item_b = CatalogItem(
        source_id=registered_source_id,
        source_key="BK-COMMIT-B",
        item_type="book",
        title_raw="Título B",
        title_norm="titulo b",
        raw_record_json={},
        current_import_id=None,
    )
    item_repo.upsert(item_a)
    item_repo.upsert(item_b)

    saved_a = item_repo.get_by_source_and_key(registered_source_id, "BK-COMMIT-A")
    saved_b = item_repo.get_by_source_and_key(registered_source_id, "BK-COMMIT-B")

    # add() faz commit internamente — registro já deve estar visível
    match_repo.add(
        left_item_id=saved_a.id or 0,
        right_item_id=saved_b.id or 0,
        score=75.0,
        rule="title_fuzzy",
        status="possible",
        confidence_band="medium",
    )

    # Verificar que o registro foi persistido e está visível na mesma conexão
    count = db_conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    assert count == 1
