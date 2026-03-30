from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Alias(BaseModel):
    id: int | None = None
    alias_kind: str
    alias_text: str
    canonical_text: str
    source_scope: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
