"""Repositório de CatalogItem com suporte a upsert null-safe.

Política de merge na atualização:
  - Campos obrigatórios (title_raw, item_type) sempre sobrescritos.
  - Campos opcionais enriquecíveis (title_norm, author_*, series_*,
    publisher_*, year, language, etc.) usam a merge policy selecionada.
  - current_import_id é sempre atualizado para o job mais recente.
  - raw_record_json sempre sobrescrito (contém o snapshot bruto completo).

A detecção de "skipped" considera o estado materializado final, não apenas o
raw_record_json. Isso evita congelar campos derivados quando aliases,
normalização ou regras de merge mudarem sem alteração no registro bruto.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.domain.value_objects.merge_policy import MergePolicy

_ALWAYS_FIELDS = ("item_type", "title_raw", "raw_record_json", "is_active")
_OPTIONAL_FIELDS = (
    "title_norm",
    "subtitle_raw",
    "author_raw",
    "author_norm",
    "series_raw",
    "series_norm",
    "publisher_raw",
    "publisher_norm",
    "year",
    "language",
    "volume",
    "edition",
    "path_or_location",
    "resource_type",
)


class CatalogItemRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, item: CatalogItem, merge_policy: MergePolicy = MergePolicy.MERGE) -> tuple[int, str]:
        """Retorna (item_id, operation) onde operation é 'inserted' | 'updated' | 'skipped'."""
        existing = self.conn.execute(
            "SELECT * FROM catalog_items WHERE source_id = ? AND source_key = ?",
            (item.source_id, item.source_key),
        ).fetchone()

        new_json = json.dumps(item.raw_record_json, ensure_ascii=False, sort_keys=True)

        if existing:
            existing_id = int(existing["id"])
            if self._matches_materialized_state(existing, item, new_json, merge_policy):
                self._refresh_current_import(existing_id, item.current_import_id)
                return existing_id, "skipped"

        operation = "updated" if existing else "inserted"
        always_fields = (
            "item_type = excluded.item_type, "
            "title_raw = excluded.title_raw, "
            "raw_record_json = excluded.raw_record_json, "
            "is_active = excluded.is_active, "
            "current_import_id = excluded.current_import_id, "
            "updated_at = CURRENT_TIMESTAMP"
        )

        if merge_policy == MergePolicy.REPLACE:
            set_clause = ", ".join([f"{field} = excluded.{field}" for field in _OPTIONAL_FIELDS])
        elif merge_policy == MergePolicy.KEEP_EXISTING:
            set_clause = ", ".join([f"{field} = {field}" for field in _OPTIONAL_FIELDS])
        else:
            set_clause = ", ".join([f"{field} = COALESCE(excluded.{field}, {field})" for field in _OPTIONAL_FIELDS])

        sql = f"""
            INSERT INTO catalog_items (
                source_id, source_key, item_type, title_raw, title_norm, subtitle_raw,
                author_raw, author_norm, series_raw, series_norm, publisher_raw, publisher_norm,
                year, language, volume, edition, path_or_location, resource_type,
                raw_record_json, is_active, current_import_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id, source_key) DO UPDATE SET
                {always_fields},
                {set_clause}
        """

        cursor = self.conn.execute(
            sql,
            (
                item.source_id,
                item.source_key,
                item.item_type,
                item.title_raw,
                item.title_norm,
                item.subtitle_raw,
                item.author_raw,
                item.author_norm,
                item.series_raw,
                item.series_norm,
                item.publisher_raw,
                item.publisher_norm,
                item.year,
                item.language,
                item.volume,
                item.edition,
                item.path_or_location,
                item.resource_type,
                new_json,
                int(item.is_active),
                item.current_import_id,
            ),
        )
        self.conn.commit()
        if existing:
            return int(existing["id"]), operation
        lastrowid = cursor.lastrowid
        if lastrowid is None:
            raise RuntimeError("Falha ao persistir item de catálogo")
        return int(lastrowid), operation

    def get_by_source_and_key(self, source_id: int, source_key: str) -> CatalogItem | None:
        """Busca um item pelo par (source_id, source_key) - chave única."""
        row = self.conn.execute(
            "SELECT * FROM catalog_items WHERE source_id = ? AND source_key = ?",
            (source_id, source_key),
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[CatalogItem]:
        rows = self.conn.execute("SELECT * FROM catalog_items ORDER BY id DESC").fetchall()
        return [self._to_entity(row) for row in rows]

    def search(self, query: str) -> list[CatalogItem]:
        rows = self.conn.execute(
            """
            SELECT c.*
            FROM catalog_items_fts f
            JOIN catalog_items c ON c.id = f.rowid
            WHERE catalog_items_fts MATCH ?
            ORDER BY rank
            """,
            (query,),
        ).fetchall()
        return [self._to_entity(row) for row in rows]

    def _matches_materialized_state(
        self,
        existing: sqlite3.Row,
        item: CatalogItem,
        new_json: str,
        merge_policy: MergePolicy,
    ) -> bool:
        expected: dict[str, Any] = {
            "item_type": item.item_type,
            "title_raw": item.title_raw,
            "raw_record_json": new_json,
            "is_active": int(item.is_active),
        }

        existing_json = json.dumps(json.loads(existing["raw_record_json"]), ensure_ascii=False, sort_keys=True)
        if existing_json != new_json:
            return False

        for field in _ALWAYS_FIELDS:
            if field == "raw_record_json":
                continue
            if existing[field] != expected[field]:
                return False

        for field in _OPTIONAL_FIELDS:
            if merge_policy == MergePolicy.REPLACE:
                expected_value = getattr(item, field)
            elif merge_policy == MergePolicy.KEEP_EXISTING:
                expected_value = existing[field]
            else:
                incoming_value = getattr(item, field)
                expected_value = incoming_value if incoming_value is not None else existing[field]

            if existing[field] != expected_value:
                return False

        return True

    def _refresh_current_import(self, item_id: int, current_import_id: int | None) -> None:
        self.conn.execute(
            """
            UPDATE catalog_items
            SET current_import_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (current_import_id, item_id),
        )
        self.conn.commit()

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> CatalogItem:
        payload = dict(row)
        payload["raw_record_json"] = json.loads(payload["raw_record_json"])
        return CatalogItem.model_validate(payload)
