from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ItemTheme(BaseModel):
    id: int | None = None
    item_id: int
    theme_id: int
    assignment_type: str = "manual"
    created_at: datetime | None = None
    updated_at: datetime | None = None
