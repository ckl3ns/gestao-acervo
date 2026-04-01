"""Streamlit app - Catálogo Unificado de Acervo (Bootstrap).

Conexão SQLite cacheada com @st.cache_resource para evitar que cada
interação do usuário recrie a conexão do zero.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import streamlit as st

from catalogo_acervo.application.use_cases.assign_theme import AssignThemeUseCase
from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    ImportSourceItemsFromSourceUseCase,
)
from catalogo_acervo.application.use_cases.list_sources import ListSourcesUseCase
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
from catalogo_acervo.config.settings import get_settings
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db
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
from catalogo_acervo.infrastructure.db.repositories.theme_repository import ThemeRepository
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger
from catalogo_acervo.interfaces.mappers.catalog_item_mapper import CatalogItemMapper
from catalogo_acervo.interfaces.mappers.source_mapper import SourceMapper

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "src/catalogo_acervo/infrastructure/db/schema.sql"


@st.cache_resource
def _get_db_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite reutilizada durante toda a sessão do processo.

    @st.cache_resource garante que get_connection() é chamado uma única vez
    por processo Streamlit, independente de quantas vezes main() roda por
    interação do usuário.
    """
    settings = get_settings()
    conn = get_connection(settings.db_path)
    init_db(conn, _SCHEMA_PATH)
    return conn


def _build_use_cases(
    conn: sqlite3.Connection,
) -> tuple[
    RegisterSourceUseCase,
    ListSourcesUseCase,
    ImportSourceItemsFromSourceUseCase,
    SearchCatalogUseCase,
    AssignThemeUseCase,
    AliasRepository,
]:
    source_repo = SourceRepository(conn)
    source_lookup = SourceLookupRepository(conn)
    alias_repo = AliasRepository(conn)
    item_repo = CatalogItemRepository(conn)
    import_repo = ImportRepository(conn)
    match_repo = MatchRepository(conn)
    theme_repo = ThemeRepository(conn)
    logger = ProcessingLogger(conn)
    parser_registry = ParserRegistry([MockParser()])
    suggest_matches_uc = SuggestMatchesUseCase(item_repo, match_repo)

    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
        suggest_matches_use_case=suggest_matches_uc,
    )
    return (
        RegisterSourceUseCase(source_repo, parser_registry),
        ListSourcesUseCase(source_repo),
        import_uc,
        SearchCatalogUseCase(item_repo),
        AssignThemeUseCase(theme_repo),
        alias_repo,
    )


def main() -> None:
    conn = _get_db_connection()
    register_source, list_sources, import_uc, search_uc, theme_uc, alias_repo = _build_use_cases(conn)

    st.title("Catálogo Unificado de Acervo - Bootstrap")
    st.caption("Importação resolvida por fonte, com parser registrado, aliases aplicados e matching incremental.")

    with st.expander("Cadastrar fonte"):
        name = st.text_input("Nome da fonte")
        source_type = st.text_input("Tipo", value="biblioteca_digital")
        parser_name = st.text_input("Parser", value="mock_csv")
        if st.button("Salvar fonte"):
            try:
                register_source.execute(name=name, source_type=source_type, parser_name=parser_name)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Fonte cadastrada")

    sources = [SourceMapper.to_dto(source).model_dump() for source in list_sources.execute()]
    st.subheader("Fontes cadastradas")
    st.write(sources)

    with st.expander("Aliases"):
        alias_kind = st.selectbox("Tipo de alias", options=["title", "author", "series", "publisher"])
        alias_text = st.text_input("Alias")
        canonical_text = st.text_input("Canônico")
        source_scope = st.text_input("Escopo do parser (opcional)", value="mock_csv")
        if st.button("Salvar alias"):
            alias_id = alias_repo.upsert(
                alias_kind=alias_kind,
                alias_text=alias_text,
                canonical_text=canonical_text,
                source_scope=source_scope or None,
            )
            st.success(f"Alias salvo. id={alias_id}")
        st.write([alias.model_dump() for alias in alias_repo.list_active()])

    with st.expander("Importar arquivo"):
        source_id_input = st.number_input("Source ID", min_value=1, step=1)
        file_path_input = st.text_input("Caminho do arquivo", value="data/samples/mock_source.csv")
        if st.button("Importar"):
            try:
                job_id = import_uc.execute(
                    source_id=int(source_id_input),
                    file_path=Path(file_path_input),
                )
            except (ValueError, FileNotFoundError) as exc:
                st.error(str(exc))
            else:
                st.success(f"Importação concluída. job_id={job_id}")

    st.subheader("Busca")
    query = st.text_input("Buscar (FTS5)", value="teologia")
    if st.button("Buscar"):
        result = [CatalogItemMapper.to_dto(item).model_dump() for item in search_uc.execute(query)]
        st.write(result)

    with st.expander("Temas"):
        theme_name = st.text_input("Novo tema", value="Teologia")
        if st.button("Criar tema"):
            theme_id = theme_uc.create_theme(theme_name)
            st.success(f"Tema criado. id={theme_id}")
        st.write([t.model_dump() for t in theme_uc.list_themes()])


if __name__ == "__main__":
    main()
