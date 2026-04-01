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

    saved_a = item_repo.get_by_source_and_key(registered_source_id, "BK-MATCH-A")
    saved_b = item_repo.get_by_source_and_key(registered_source_id, "BK-MATCH-B")
    assert saved_a is not None
    assert saved_b is not None

    match_id = match_repo.add(
        left_item_id=saved_a.id or 0,
        right_item_id=saved_b.id or 0,
        score=95.5,
        rule="title+author_fuzzy",
        status="possible",
        confidence_band="high",
    )

    assert match_id is not None
    row = db_conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    assert row is not None
    assert row["left_item_id"] == min(saved_a.id, saved_b.id)
    assert row["right_item_id"] == max(saved_a.id, saved_b.id)
    assert row["match_score"] == 95.5
    assert row["match_rule"] == "title+author_fuzzy"
    assert row["status"] == "possible"
    assert row["confidence_band"] == "high"


def test_add_returns_lastrowid_for_insert(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """add() deve retornar o id da linha inserida quando cria um match novo."""
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
    assert saved_a is not None
    assert saved_b is not None

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


def test_add_returns_none_when_insert_is_ignored(
    db_conn: sqlite3.Connection,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """INSERT OR IGNORE deve retornar None quando o par já existe."""
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-1", "book", "Title 1", "{}"),
    )
    item1_id = int(cursor.lastrowid)
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-2", "book", "Title 2", "{}"),
    )
    item2_id = int(cursor.lastrowid)
    db_conn.commit()

    first_id = match_repo.add(item1_id, item2_id, 90.0, "title", "possible", "high")
    second_id = match_repo.add(item1_id, item2_id, 90.0, "title", "possible", "high")

    assert first_id is not None
    assert second_id is None


def test_match_duplicate_insert_ignored_symmetrically(
    db_conn: sqlite3.Connection,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """Inserir o mesmo par invertido não deve criar duplicata simétrica."""
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-3", "book", "Title 3", "{}"),
    )
    item1_id = int(cursor.lastrowid)
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-4", "book", "Title 4", "{}"),
    )
    item2_id = int(cursor.lastrowid)
    db_conn.commit()

    match_repo.add(item1_id, item2_id, 90.0, "title", "possible", "high")
    match_repo.add(item2_id, item1_id, 90.0, "title", "possible", "high")

    count = db_conn.execute(
        "SELECT COUNT(*) FROM matches WHERE left_item_id = ? AND right_item_id = ?",
        (min(item1_id, item2_id), max(item1_id, item2_id)),
    ).fetchone()[0]
    assert count == 1


def test_match_no_exception_on_duplicate(
    db_conn: sqlite3.Connection,
    match_repo: MatchRepository,
    registered_source_id: int,
) -> None:
    """Segunda inserção do mesmo par não deve lançar exceção."""
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-5", "book", "Title 5", "{}"),
    )
    item1_id = int(cursor.lastrowid)
    cursor = db_conn.execute(
        "INSERT INTO catalog_items (source_id, source_key, item_type, title_raw, raw_record_json) VALUES (?, ?, ?, ?, ?)",
        (registered_source_id, "key-6", "book", "Title 6", "{}"),
    )
    item2_id = int(cursor.lastrowid)
    db_conn.commit()

    match_repo.add(item1_id, item2_id, 90.0, "title", "possible", "high")
    match_repo.add(item1_id, item2_id, 90.0, "title", "possible", "high")
