from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.source import Source


class SourceRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, source: Source) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO sources (name, source_type, parser_name, description, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source.name, source.source_type, source.parser_name, source.description, int(source.is_active)),
        )
        self.conn.commit()
        lastrowid = cursor.lastrowid
        if lastrowid is None:
            raise RuntimeError("Falha ao persistir fonte")
        return int(lastrowid)

    def list_all(self) -> list[Source]:
        rows = self.conn.execute("SELECT * FROM sources ORDER BY created_at DESC").fetchall()
        return [Source.model_validate(dict(row)) for row in rows]
