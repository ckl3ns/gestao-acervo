from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.theme import Theme


class ThemeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, theme: Theme) -> int:
        cursor = self.conn.execute(
            "INSERT INTO themes (name, slug, description) VALUES (?, ?, ?)",
            (theme.name, theme.slug, theme.description),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def list_all(self) -> list[Theme]:
        rows = self.conn.execute("SELECT * FROM themes ORDER BY name").fetchall()
        return [Theme.model_validate(dict(row)) for row in rows]

    def assign_item(self, item_id: int, theme_id: int, assignment_type: str = "manual") -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO item_themes (item_id, theme_id, assignment_type)
            VALUES (?, ?, ?)
            """,
            (item_id, theme_id, assignment_type),
        )
        self.conn.commit()
