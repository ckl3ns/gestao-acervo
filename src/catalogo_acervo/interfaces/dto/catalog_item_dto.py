from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CatalogItemDTO(BaseModel):
    """DTO para transferência de dados de CatalogItem entre camadas."""

    id: int | None = None
    source_id: int
    source_key: str
    item_type: str
    title_raw: str
    title_norm: str | None = None
    subtitle_raw: str | None = None
    author_raw: str | None = None
    author_norm: str | None = None
    series_raw: str | None = None
    publisher_raw: str | None = None
    year: int | None = None
    language: str | None = None
    path_or_location: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
