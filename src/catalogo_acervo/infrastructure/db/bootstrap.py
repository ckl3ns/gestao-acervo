from __future__ import annotations

from pathlib import Path

from catalogo_acervo.config.settings import get_settings
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db


def bootstrap_db() -> None:
    settings = get_settings()
    conn = get_connection(settings.db_path)
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    init_db(conn, schema_path)


if __name__ == "__main__":
    bootstrap_db()
