"""Testes unitários para incrementalidade do SuggestMatchesUseCase.

Validates: Requirements 2.3, 2.4, 2.5
"""

from __future__ import annotations

import sqlite3

from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository


def _insert_source(db_conn: sqlite3.Connection, name: str, parser_name: str) -> int:
    cursor = db_conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        (name, "mock", parser_name),
    )
    db_conn.commit()
    return int(cursor.lastrowid)


def _count_matches(db_conn: sqlite3.Connection) -> int:
    row = db_conn.execute("SELECT COUNT(*) FROM matches").fetchone()
    return int(row[0])


def test_suggest_matches_incremental_only_processes_affected(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
) -> None:
    """Apenas IDs afetados são processados; itens fora do conjunto não geram matches."""
    source_a_id = _insert_source(db_conn, "Source A", "mock_csv_a")
    source_b_id = _insert_source(db_conn, "Source B", "mock_csv_b")

    item_a_id, _ = item_repo.upsert(
        CatalogItem(
            source_id=source_a_id,
            source_key="key-a",
            item_type="book",
            title_raw="Introdução à Teologia",
            title_norm="introducao a teologia",
            author_raw="João Silva",
            author_norm="joao silva",
            raw_record_json={},
        )
    )
    item_repo.upsert(
        CatalogItem(
            source_id=source_b_id,
            source_key="key-b",
            item_type="book",
            title_raw="Introdução à Teologia",
            title_norm="introducao a teologia",
            author_raw="João Silva",
            author_norm="joao silva",
            raw_record_json={},
        )
    )
    item_c_id, _ = item_repo.upsert(
        CatalogItem(
            source_id=source_a_id,
            source_key="key-c",
            item_type="book",
            title_raw="Culinária Avançada para Chefs",
            title_norm="culinaria avancada para chefs",
            author_raw="Maria Souza",
            author_norm="maria souza",
            raw_record_json={},
        )
    )

    suggest_uc = SuggestMatchesUseCase(item_repo, match_repo)
    created = suggest_uc.execute(affected_item_ids=[item_a_id])

    matches_involving_a = db_conn.execute(
        "SELECT COUNT(*) FROM matches WHERE left_item_id = ? OR right_item_id = ?",
        (item_a_id, item_a_id),
    ).fetchone()[0]
    assert created == 1
    assert matches_involving_a == 1

    matches_involving_c = db_conn.execute(
        "SELECT COUNT(*) FROM matches WHERE left_item_id = ? OR right_item_id = ?",
        (item_c_id, item_c_id),
    ).fetchone()[0]
    assert matches_involving_c == 0


def test_suggest_matches_idempotent_on_no_change(
    db_conn: sqlite3.Connection,
    item_repo: CatalogItemRepository,
    match_repo: MatchRepository,
) -> None:
    """Segunda execução sem mudança não cria novas linhas."""
    source_a_id = _insert_source(db_conn, "Source A", "mock_csv_a")
    source_b_id = _insert_source(db_conn, "Source B", "mock_csv_b")

    item_repo.upsert(
        CatalogItem(
            source_id=source_a_id,
            source_key="key-1",
            item_type="book",
            title_raw="Introdução à Teologia",
            title_norm="introducao a teologia",
            author_raw="João Silva",
            author_norm="joao silva",
            raw_record_json={},
        )
    )
    item_repo.upsert(
        CatalogItem(
            source_id=source_b_id,
            source_key="key-2",
            item_type="book",
            title_raw="Introdução à Teologia",
            title_norm="introducao a teologia",
            author_raw="João Silva",
            author_norm="joao silva",
            raw_record_json={},
        )
    )

    suggest_uc = SuggestMatchesUseCase(item_repo, match_repo)

    created_first = suggest_uc.execute()
    count_after_first = _count_matches(db_conn)

    created_second = suggest_uc.execute()
    count_after_second = _count_matches(db_conn)

    assert created_first == 1
    assert count_after_first == 1
    assert created_second == 0
    assert count_after_second == count_after_first
