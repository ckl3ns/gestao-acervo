"""Testes unitários para semântica de importação.

Validates: Requirements 1.1, 1.5, 1.7
"""

from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.import_job import ImportJob
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository


def test_import_job_default_mode() -> None:
    """ImportJob deve ter import_mode == 'upsert' por padrão."""
    job = ImportJob(source_id=1)
    assert job.import_mode == "upsert"


def test_finish_persists_updated_skipped(
    db_conn: sqlite3.Connection, import_repo: ImportRepository
) -> None:
    """finish() deve persistir todos os contadores corretamente no banco."""
    # Cria fonte para satisfazer FK
    cursor = db_conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("Fonte Teste", "mock", "mock_csv"),
    )
    db_conn.commit()
    source_id = int(cursor.lastrowid)

    job_id = import_repo.create(ImportJob(source_id=source_id, status="running"))
    import_repo.finish(job_id, "completed", 10, 3, 4, 2, 1)

    row = db_conn.execute(
        "SELECT status, total_read, total_inserted, total_updated, total_skipped, total_errors "
        "FROM imports WHERE id = ?",
        (job_id,),
    ).fetchone()

    assert row["status"] == "completed"
    assert row["total_read"] == 10
    assert row["total_inserted"] == 3
    assert row["total_updated"] == 4
    assert row["total_skipped"] == 2
    assert row["total_errors"] == 1


def test_counter_conservation(
    db_conn: sqlite3.Connection, import_repo: ImportRepository
) -> None:
    """inserted + updated + skipped + errors deve ser igual a total_read."""
    cursor = db_conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("Fonte Conservação", "mock", "mock_csv"),
    )
    db_conn.commit()
    source_id = int(cursor.lastrowid)

    job_id = import_repo.create(ImportJob(source_id=source_id, status="running"))
    total_read, inserted, updated, skipped, errors = 20, 5, 8, 4, 3
    import_repo.finish(job_id, "completed", total_read, inserted, updated, skipped, errors)

    row = db_conn.execute(
        "SELECT total_read, total_inserted, total_updated, total_skipped, total_errors "
        "FROM imports WHERE id = ?",
        (job_id,),
    ).fetchone()

    assert (
        row["total_inserted"] + row["total_updated"] + row["total_skipped"] + row["total_errors"]
        == row["total_read"]
    )
