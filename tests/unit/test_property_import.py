"""Property-based tests for import pipeline integrity.

Feature: core-integrity-fixes, Property 1: counter conservation invariant
Feature: core-integrity-fixes, Property 2: upsert counter correctness
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.domain.entities.import_job import ImportJob
from catalogo_acervo.infrastructure.db.connection import init_db
from catalogo_acervo.infrastructure.db.repositories.alias_repository import AliasRepository
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_lookup_repository import (
    SourceLookupRepository,
)
from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

SCHEMA_PATH = Path("src/catalogo_acervo/infrastructure/db/schema.sql")
PARSER_NAME = "prop_test_parser"


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn, SCHEMA_PATH)
    return conn


def _make_source(conn: sqlite3.Connection) -> int:
    cursor = conn.execute(
        "INSERT INTO sources (name, source_type, parser_name) VALUES (?, ?, ?)",
        ("PropTestSource", "mock", PARSER_NAME),
    )
    conn.commit()
    return int(cursor.lastrowid)


class _InlineParser(BaseParser):
    parser_name = PARSER_NAME

    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records

    def parse(self, file_path: Path) -> list[dict[str, Any]]:
        return self._records


@settings(max_examples=100)
@given(
    st.lists(
        st.text(min_size=1, alphabet=st.characters(whitelist_categories=("L",))),
        min_size=0,
        max_size=20,
    )
)
def test_property_counter_conservation(titles: list[str]) -> None:
    """For any import run, inserted + updated + skipped + errors == total_read."""
    conn = _make_conn()
    try:
        source_id = _make_source(conn)
        records = [
            {"title": title, "source_key": f"key-{i}", "item_type": "book"}
            for i, title in enumerate(titles)
        ]

        parser = _InlineParser(records)
        registry = ParserRegistry([parser])
        use_case = ImportSourceItemsFromSourceUseCase(
            source_lookup=SourceLookupRepository(conn),
            alias_lookup=AliasRepository(conn),
            parser_registry=registry,
            import_repository=ImportRepository(conn),
            item_repository=CatalogItemRepository(conn),
            logger=ProcessingLogger(conn),
        )

        job_id = use_case.execute(source_id, Path("dummy.csv"))
        row = conn.execute(
            "SELECT total_read, total_inserted, total_updated, total_skipped, total_errors "
            "FROM imports WHERE id = ?",
            (job_id,),
        ).fetchone()

        assert row is not None
        assert (
            row["total_inserted"] + row["total_updated"] + row["total_skipped"] + row["total_errors"]
            == row["total_read"]
        )
    finally:
        conn.close()


@settings(max_examples=100)
@given(st.booleans())
def test_property_upsert_counter_new_vs_existing(item_exists: bool) -> None:
    """If (source_id, source_key) already existed -> updated; if not -> inserted."""
    conn = _make_conn()
    try:
        source_id = _make_source(conn)
        item_repo = CatalogItemRepository(conn)
        import_repo = ImportRepository(conn)
        job_id = import_repo.create(ImportJob(source_id=source_id, status="running"))

        from catalogo_acervo.domain.entities.catalog_item import CatalogItem

        source_key = "prop-key-001"
        if item_exists:
            first_item = CatalogItem(
                source_id=source_id,
                source_key=source_key,
                title_raw="Original Title",
                raw_record_json={"title": "Original Title", "source_key": source_key},
                current_import_id=job_id,
            )
            _, op = item_repo.upsert(first_item)
            assert op == "inserted"

            second_item = CatalogItem(
                source_id=source_id,
                source_key=source_key,
                title_raw="Updated Title",
                raw_record_json={"title": "Updated Title", "source_key": source_key},
                current_import_id=job_id,
            )
            _, op2 = item_repo.upsert(second_item)
            assert op2 == "updated"
        else:
            new_item = CatalogItem(
                source_id=source_id,
                source_key=source_key,
                title_raw="Brand New Title",
                raw_record_json={"title": "Brand New Title", "source_key": source_key},
                current_import_id=job_id,
            )
            _, op = item_repo.upsert(new_item)
            assert op == "inserted"
    finally:
        conn.close()


@settings(max_examples=100)
@given(st.booleans())
def test_property_upsert_skipped_on_identical_content(run_twice: bool) -> None:
    """Upserting identical content always yields 'skipped'."""
    conn = _make_conn()
    try:
        source_id = _make_source(conn)
        item_repo = CatalogItemRepository(conn)
        import_repo = ImportRepository(conn)
        job_id = import_repo.create(ImportJob(source_id=source_id, status="running"))

        from catalogo_acervo.domain.entities.catalog_item import CatalogItem

        item = CatalogItem(
            source_id=source_id,
            source_key="prop-key-identical",
            title_raw="Same Title",
            raw_record_json={"title": "Same Title", "source_key": "prop-key-identical"},
            current_import_id=job_id,
        )
        _, op1 = item_repo.upsert(item)
        assert op1 == "inserted"

        if run_twice:
            _, op2 = item_repo.upsert(item)
            assert op2 == "skipped"
    finally:
        conn.close()
