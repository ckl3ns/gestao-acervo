from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.source import Source


class SourceLookupRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_by_id(self, source_id: int) -> Source | None:
        row = self.conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        if row is None:
            return None
        return Source.model_validate(dict(row))
