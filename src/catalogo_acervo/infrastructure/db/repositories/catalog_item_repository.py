from __future__ import annotations

import json
import sqlite3

from catalogo_acervo.domain.entities.catalog_item import CatalogItem


class CatalogItemRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, item: CatalogItem) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO catalog_items (
                source_id, source_key, item_type, title_raw, title_norm, subtitle_raw,
                author_raw, author_norm, series_raw, series_norm, publisher_raw, publisher_norm,
                year, language, volume, edition, path_or_location, resource_type,
                raw_record_json, is_active, current_import_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id, source_key) DO UPDATE SET
                item_type = excluded.item_type,
                title_raw = excluded.title_raw,
                title_norm = excluded.title_norm,
                subtitle_raw = excluded.subtitle_raw,
                author_raw = excluded.author_raw,
                author_norm = excluded.author_norm,
                series_raw = excluded.series_raw,
                series_norm = excluded.series_norm,
                publisher_raw = excluded.publisher_raw,
                publisher_norm = excluded.publisher_norm,
                year = excluded.year,
                language = excluded.language,
                volume = excluded.volume,
                edition = excluded.edition,
                path_or_location = excluded.path_or_location,
                resource_type = excluded.resource_type,
                raw_record_json = excluded.raw_record_json,
                is_active = excluded.is_active,
                current_import_id = excluded.current_import_id,
                updated_at = CURRENT_TIMESTAMP
            """,
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
                json.dumps(item.raw_record_json, ensure_ascii=False),
                int(item.is_active),
                item.current_import_id,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

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
