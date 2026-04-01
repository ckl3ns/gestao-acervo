from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProcessingLog(BaseModel):
    id: int | None = None
    source_id: int | None = None
    import_id: int | None = None
    level: str = "INFO"
    message: str
    context_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
