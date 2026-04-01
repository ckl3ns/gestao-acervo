from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ImportJob(BaseModel):
    id: int | None = None
    source_id: int
    import_mode: str = "upsert"
    imported_at: datetime | None = None
    status: str = "pending"
    total_read: int = 0
    total_inserted: int = 0
    total_updated: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    raw_file_name: str | None = None
