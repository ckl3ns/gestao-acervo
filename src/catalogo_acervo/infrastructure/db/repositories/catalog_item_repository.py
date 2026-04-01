"""Repositório de CatalogItem com suporte a upsert null-safe.

Política de merge na atualização (fundação do WI-002):
  - Campos obrigatórios (title_raw, item_type) sempre sobrescritos.
  - Campos opcionais enriquecíveis (title_norm, author_*, series_*,
    publisher_*, year, language, etc.) usam COALESCE:
    se o novo valor não for NULL, atualiza; caso contrário, preserva o
    valor existente.
  - current_import_id e updated_at sempre atualizados.
  - raw_record_json sempre sobrescrito (contém o snapshot bruto completo).

Isso evita que uma reimportação parcial apague campos válidos já
persistidos de uma importação anterior mais completa.
"""

from __future__ import annotations

import json
import sqlite3

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.domain.value_objects.merge_policy import MergePolicy


class CatalogItemRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, item: CatalogItem, merge_policy: MergePolicy = MergePolicy.MERGE) -> tuple[int, str]:
        """Retorna (item_id, operation) onde operation é 'inserted' | 'updated' | 'skipped'."""
        existing = self.conn.execute(
            "SELECT id, raw_record_json FROM catalog_items WHERE source_id = ? AND source_key = ?",
            (item.source_id, item.source_key),
        ).fetchone()

        new_json = json.dumps(item.raw_record_json, ensure_ascii=False, sort_keys=True)

        if existing:
            existing_normalized = json.dumps(
                json.loads(existing["raw_record_json"]), ensure_ascii=False, sort_keys=True
            )
            if existing_normalized == new_json:
                return int(existing["id"]), "skipped"

        operation = "updated" if existing else "inserted"

        always_fields = "item_type = excluded.item_type, title_raw = excluded.title_raw, raw_record_json = excluded.raw_record_json, is_active = excluded.is_active, current_import_id = excluded.current_import_id, updated_at = CURRENT_TIMESTAMP"

        optional_fields = [
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
        ]

        if merge_policy == MergePolicy.REPLACE:
            set_clause = ", ".join([f"{f} = excluded.{f}" for f in optional_fields])
        elif merge_policy == MergePolicy.KEEP_EXISTING:
            set_clause = ", ".join([f"{f} = {f}" for f in optional_fields])
        else:
            set_clause = ", ".join([f"{f} = COALESCE(excluded.{f}, {f})" for f in optional_fields])

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
        return int(cursor.lastrowid or 0), operation

    def get_by_source_and_key(self, source_id: int, source_key: str) -> CatalogItem | None:
        """Busca um item pelo par (source_id, source_key) — chave única."""
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

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> CatalogItem:
        payload = dict(row)
        payload["raw_record_json"] = json.loads(payload["raw_record_json"])
        return CatalogItem.model_validate(payload)
