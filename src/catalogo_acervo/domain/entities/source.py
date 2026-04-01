from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Source(BaseModel):
    id: int | None = None
    name: str
    source_type: str
    parser_name: str
    description: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
