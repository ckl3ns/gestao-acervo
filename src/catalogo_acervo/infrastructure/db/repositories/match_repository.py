from __future__ import annotations

import sqlite3


class MatchRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, left_item_id: int, right_item_id: int, score: float, rule: str, status: str, confidence_band: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO matches (left_item_id, right_item_id, match_score, match_rule, status, confidence_band)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (left_item_id, right_item_id, score, rule, status, confidence_band),
        )
        self.conn.commit()
        return int(cursor.lastrowid)
