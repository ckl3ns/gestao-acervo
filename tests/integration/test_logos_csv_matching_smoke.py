from __future__ import annotations

import sqlite3
from pathlib import Path

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
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
from catalogo_acervo.infrastructure.ingestion.parsers.logos_csv_parser import (
    LogosCsvParser,
)
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

_LOGOS10_MATCHING_SAMPLE = Path("data/samples/logos10_matching_sample.csv")
_LOGOS7_MATCHING_SAMPLE = Path("data/samples/logos7_matching_sample.csv")


def test_realistic_logos_samples_produce_match_candidates(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
    source_lookup: SourceLookupRepository,
    alias_repo: AliasRepository,
    item_repo: CatalogItemRepository,
    import_repo: ImportRepository,
    match_repo: MatchRepository,
    logger: ProcessingLogger,
) -> None:
    parser_registry = ParserRegistry([LogosCsvParser()])
    source_a_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Logos 10 sample",
        source_type="biblioteca_digital",
        parser_name="logos_csv",
    )
    source_b_id = RegisterSourceUseCase(source_repo, parser_registry).execute(
        name="Logos 7 sample",
        source_type="biblioteca_digital",
        parser_name="logos_csv",
    )

    suggest_uc = SuggestMatchesUseCase(items_repo=item_repo, match_repo=match_repo)
    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
        suggest_matches_use_case=suggest_uc,
    )

    import_uc.execute(source_id=source_a_id, file_path=_LOGOS10_MATCHING_SAMPLE)
    import_uc.execute(source_id=source_b_id, file_path=_LOGOS7_MATCHING_SAMPLE)

    source_a_item = item_repo.get_by_source_and_key(source_a_id, "LLS:ZPHDICTCHRSPIRIT")
    source_b_item = item_repo.get_by_source_and_key(source_b_id, "LLS:ZPHDICTCHRSPIRIT")
    assert source_a_item is not None
    assert source_b_item is not None
    assert source_a_item.id is not None
    assert source_b_item.id is not None

    left_id, right_id = sorted((source_a_item.id, source_b_item.id))
    match_row = db_conn.execute(
        """
        SELECT match_score, match_rule, status, confidence_band
        FROM matches
        WHERE left_item_id = ? AND right_item_id = ?
        """,
        (left_id, right_id),
    ).fetchone()

    assert match_row is not None
    assert match_row["match_rule"] == "title+author_fuzzy"
    assert match_row["status"] == "possible"
    assert float(match_row["match_score"]) >= 85.0
