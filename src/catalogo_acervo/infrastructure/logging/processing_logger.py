from __future__ import annotations

import json
import sqlite3
from typing import Any


class ProcessingLogger:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def log(self, message: str, level: str = "INFO", source_id: int | None = None, import_id: int | None = None, context: dict[str, Any] | None = None) -> None:
        self.conn.execute(
            """
            INSERT INTO processing_logs (source_id, import_id, level, message, context_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, import_id, level, message, json.dumps(context or {}, ensure_ascii=False)),
        )
        self.conn.commit()
