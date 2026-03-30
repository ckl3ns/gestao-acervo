from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CatalogItem(BaseModel):
    id: int | None = None
    source_id: int
    source_key: str
    item_type: str = "other"
    title_raw: str
    title_norm: str | None = None
    subtitle_raw: str | None = None
    author_raw: str | None = None
    author_norm: str | None = None
    series_raw: str | None = None
    series_norm: str | None = None
    publisher_raw: str | None = None
    publisher_norm: str | None = None
    year: int | None = None
    language: str | None = None
    volume: str | None = None
    edition: str | None = None
    path_or_location: str | None = None
    resource_type: str | None = None
    raw_record_json: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    current_import_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
