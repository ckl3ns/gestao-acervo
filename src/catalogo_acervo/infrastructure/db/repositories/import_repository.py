from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.import_job import ImportJob


class ImportRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, job: ImportJob) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO imports (source_id, import_mode, status, raw_file_name)
            VALUES (?, ?, ?, ?)
            """,
            (job.source_id, job.import_mode, job.status, job.raw_file_name),
        )
        self.conn.commit()
        lastrowid = cursor.lastrowid
        if lastrowid is None:
            raise RuntimeError("Falha ao criar job de importação")
        return int(lastrowid)

    def finish(self, job_id: int, status: str, total_read: int, total_inserted: int, total_updated: int, total_skipped: int, total_errors: int) -> None:
        self.conn.execute(
            """
            UPDATE imports
            SET status = ?, total_read = ?, total_inserted = ?, total_updated = ?, total_skipped = ?, total_errors = ?
            WHERE id = ?
            """,
            (status, total_read, total_inserted, total_updated, total_skipped, total_errors, job_id),
        )
        self.conn.commit()
