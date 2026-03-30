from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ManualReview(BaseModel):
    id: int | None = None
    left_item_id: int
    right_item_id: int
    decision: str
    note: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
