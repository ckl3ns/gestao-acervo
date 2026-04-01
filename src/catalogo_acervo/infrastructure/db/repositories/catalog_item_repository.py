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
                item_type          = excluded.item_type,
                title_raw          = excluded.title_raw,
                raw_record_json    = excluded.raw_record_json,
                is_active          = excluded.is_active,
                current_import_id  = excluded.current_import_id,
                updated_at         = CURRENT_TIMESTAMP,
                -- Campos opcionais: preserva valor existente se novo for NULL (null-safe merge)
                title_norm         = COALESCE(excluded.title_norm,      title_norm),
                subtitle_raw       = COALESCE(excluded.subtitle_raw,    subtitle_raw),
                author_raw         = COALESCE(excluded.author_raw,      author_raw),
                author_norm        = COALESCE(excluded.author_norm,     author_norm),
                series_raw         = COALESCE(excluded.series_raw,      series_raw),
                series_norm        = COALESCE(excluded.series_norm,     series_norm),
                publisher_raw      = COALESCE(excluded.publisher_raw,   publisher_raw),
                publisher_norm     = COALESCE(excluded.publisher_norm,  publisher_norm),
                year               = COALESCE(excluded.year,            year),
                language           = COALESCE(excluded.language,        language),
                volume             = COALESCE(excluded.volume,          volume),
                edition            = COALESCE(excluded.edition,         edition),
                path_or_location   = COALESCE(excluded.path_or_location, path_or_location),
                resource_type      = COALESCE(excluded.resource_type,   resource_type)
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
        return int(cursor.lastrowid or 0)

    def get_by_source_and_key(self, source_id: int, source_key: str) -> CatalogItem | None:
        """Busca um item pelo par (source_id, source_key) — chave única."""
        row = self.conn.execute(
            "SELECT * FROM catalog_items WHERE source_id = ? AND source_key = ?",
            (source_id, source_key),
        ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[CatalogItem]:
        rows = self.conn.execute(
            "SELECT * FROM catalog_items ORDER BY id DESC"
        ).fetchall()
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
