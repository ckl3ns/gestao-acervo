from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Theme(BaseModel):
    id: int | None = None
    name: str
    slug: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
