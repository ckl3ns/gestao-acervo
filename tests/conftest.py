"""Fixtures compartilhadas para todos os testes.

O fixture `db_conn` fornece uma conexão SQLite em memória com o schema
completo já inicializado. É function-scoped por padrão para garantir
isolamento entre testes.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository
from catalogo_acervo.infrastructure.db.repositories.source_lookup_repository import (
    SourceLookupRepository,
)
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.ingestion.parsers.logos_csv_parser import LogosCsvParser
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")


@pytest.fixture()
def db_conn() -> Iterator[sqlite3.Connection]:
    """Conexão SQLite em memória com schema completo aplicado.

    Cada teste recebe uma instância isolada - sem arquivo em disco,
    sem estado compartilhado entre casos de teste.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def source_repo(db_conn: sqlite3.Connection) -> SourceRepository:
    return SourceRepository(db_conn)


@pytest.fixture()
def source_lookup(db_conn: sqlite3.Connection) -> SourceLookupRepository:
    return SourceLookupRepository(db_conn)


@pytest.fixture()
def alias_repo(db_conn: sqlite3.Connection) -> AliasRepository:
    return AliasRepository(db_conn)


@pytest.fixture()
def item_repo(db_conn: sqlite3.Connection) -> CatalogItemRepository:
    return CatalogItemRepository(db_conn)


@pytest.fixture()
def import_repo(db_conn: sqlite3.Connection) -> ImportRepository:
    return ImportRepository(db_conn)


@pytest.fixture()
def match_repo(db_conn: sqlite3.Connection) -> MatchRepository:
    return MatchRepository(db_conn)


@pytest.fixture()
def logger(db_conn: sqlite3.Connection) -> ProcessingLogger:
    return ProcessingLogger(db_conn)


@pytest.fixture()
def parser_registry() -> ParserRegistry:
    return ParserRegistry([MockParser(), LogosCsvParser()])


@pytest.fixture()
def registered_source_id(db_conn: sqlite3.Connection) -> int:
    """Insere uma fonte mínima e retorna seu ID.

    Útil para testes de repositório que precisam satisfazer
    a FK constraint de catalog_items.source_id.
    """
    cursor = db_conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("Test Source", "mock", "mock_csv"),
    )
    db_conn.commit()
    return int(cursor.lastrowid)
