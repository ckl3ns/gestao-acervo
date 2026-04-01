"""Testes unitários: use cases básicos (ListSources, AssignTheme)."""

from __future__ import annotations

import sqlite3

from catalogo_acervo.application.use_cases.assign_theme import AssignThemeUseCase
from catalogo_acervo.application.use_cases.list_sources import ListSourcesUseCase
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.db.repositories.theme_repository import ThemeRepository

# ── ListSourcesUseCase ─────────────────────────────────────────────────────────


def test_list_sources_returns_empty_on_fresh_db(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
) -> None:
    result = ListSourcesUseCase(source_repo).execute()
    assert result == []


def test_list_sources_returns_registered_source(
    db_conn: sqlite3.Connection,
    source_repo: SourceRepository,
) -> None:
    RegisterSourceUseCase(source_repo).execute(
        name="Logos 10",
        source_type="logos",
        parser_name="logos_csv",
    )
    sources = ListSourcesUseCase(source_repo).execute()
    assert len(sources) == 1
    assert sources[0].name == "Logos 10"
    assert sources[0].parser_name == "logos_csv"


# ── AssignThemeUseCase ─────────────────────────────────────────────────────────


def test_create_theme_returns_id(db_conn: sqlite3.Connection) -> None:
    repo = ThemeRepository(db_conn)
    uc = AssignThemeUseCase(repo)
    theme_id = uc.create_theme("Teologia Sistemática")
    assert isinstance(theme_id, int)
    assert theme_id > 0


def test_create_theme_slug_is_derived_from_name(db_conn: sqlite3.Connection) -> None:
    repo = ThemeRepository(db_conn)
    uc = AssignThemeUseCase(repo)
    uc.create_theme("Teologia Bíblica")
    themes = uc.list_themes()
    assert len(themes) == 1
    # slug deve ser minúsculo e sem diacríticos
    assert themes[0].slug == "teologia-biblica"


def test_list_themes_empty_on_fresh_db(db_conn: sqlite3.Connection) -> None:
    repo = ThemeRepository(db_conn)
    result = AssignThemeUseCase(repo).list_themes()
    assert result == []


def test_list_themes_returns_multiple(db_conn: sqlite3.Connection) -> None:
    repo = ThemeRepository(db_conn)
    uc = AssignThemeUseCase(repo)
    uc.create_theme("Exegese")
    uc.create_theme("Hermenêutica")
    themes = uc.list_themes()
    assert len(themes) == 2
    names = {t.name for t in themes}
    assert "Exegese" in names
    assert "Hermenêutica" in names
