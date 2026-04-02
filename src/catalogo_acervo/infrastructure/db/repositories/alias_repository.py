from __future__ import annotations

import sqlite3

from catalogo_acervo.domain.entities.alias import Alias
from catalogo_acervo.domain.services.normalization import normalize_text


class AliasRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(
        self,
        *,
        alias_kind: str,
        alias_text: str,
        canonical_text: str,
        source_scope: str | None = None,
    ) -> int:
        normalized_alias = normalize_text(alias_text)
        normalized_canonical = normalize_text(canonical_text)
        if normalized_alias is None or normalized_canonical is None:
            raise ValueError("Alias e canonical_text precisam ser válidos")

        existing = self.conn.execute(
            """
            SELECT id
            FROM aliases
            WHERE alias_kind = ? AND alias_text = ? AND COALESCE(source_scope, '') = COALESCE(?, '')
            """,
            (alias_kind, normalized_alias, source_scope),
        ).fetchone()

        if existing:
            alias_id = int(existing["id"])
            self.conn.execute(
                """
                UPDATE aliases
                SET canonical_text = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (normalized_canonical, alias_id),
            )
            self.conn.commit()
            return alias_id

        cursor = self.conn.execute(
            """
            INSERT INTO aliases (alias_kind, alias_text, canonical_text, source_scope, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (alias_kind, normalized_alias, normalized_canonical, source_scope),
        )
        self.conn.commit()
        lastrowid = cursor.lastrowid
        if lastrowid is None:
            raise RuntimeError("Falha ao persistir alias")
        return int(lastrowid)

    def list_active(self) -> list[Alias]:
        rows = self.conn.execute(
            """
            SELECT * FROM aliases
            WHERE is_active = 1
            ORDER BY
                CASE WHEN source_scope IS NULL THEN 1 ELSE 0 END,
                alias_kind,
                alias_text
            """
        ).fetchall()
        return [Alias.model_validate(dict(row)) for row in rows]
