from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    db_path: Path = Field(default=Path("data/db/catalogo_acervo.db"))



def get_settings() -> Settings:
    raw_path = os.getenv("CATALOGO_DB_PATH", "data/db/catalogo_acervo.db")
    return Settings(db_path=Path(raw_path))
