from __future__ import annotations

import sqlite3


class MatchRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    @staticmethod
    def canonicalize_pair(left_item_id: int, right_item_id: int) -> tuple[int, int]:
        if left_item_id == right_item_id:
            raise ValueError("Match requer dois itens distintos")
        ordered = sorted((left_item_id, right_item_id))
        return ordered[0], ordered[1]

    def add(
        self,
        left_item_id: int,
        right_item_id: int,
        score: float,
        rule: str,
        status: str,
        confidence_band: str,
    ) -> int | None:
        left_id, right_id = self.canonicalize_pair(left_item_id, right_item_id)
        cursor = self.conn.execute(
            """
            INSERT OR IGNORE INTO matches (left_item_id, right_item_id, match_score, match_rule, status, confidence_band)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (left_id, right_id, score, rule, status, confidence_band),
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        lastrowid = cursor.lastrowid
        if lastrowid is None:
            raise RuntimeError("Falha ao persistir match")
        return int(lastrowid)
