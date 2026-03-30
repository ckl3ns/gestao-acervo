from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Match(BaseModel):
    id: int | None = None
    left_item_id: int
    right_item_id: int
    match_score: float
    match_rule: str
    status: str = "possible"
    confidence_band: str = "medium"
    created_at: datetime | None = None
    updated_at: datetime | None = None
