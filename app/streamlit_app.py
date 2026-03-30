from __future__ import annotations

from pathlib import Path

import streamlit as st

from catalogo_acervo.application.use_cases.assign_theme import AssignThemeUseCase
from catalogo_acervo.application.use_cases.import_source_items import ImportSourceItemsUseCase
from catalogo_acervo.application.use_cases.list_sources import ListSourcesUseCase
from catalogo_acervo.application.use_cases.register_source import RegisterSourceUseCase
from catalogo_acervo.application.use_cases.search_catalog import SearchCatalogUseCase
from catalogo_acervo.config.settings import get_settings
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import CatalogItemRepository
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.db.repositories.theme_repository import ThemeRepository
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger


def main() -> None:
    settings = get_settings()
    conn = get_connection(settings.db_path)
    schema_path = Path(__file__).resolve().parents[1] / "src/catalogo_acervo/infrastructure/db/schema.sql"
    init_db(conn, schema_path)

    source_repo = SourceRepository(conn)
    item_repo = CatalogItemRepository(conn)
    import_repo = ImportRepository(conn)
    theme_repo = ThemeRepository(conn)
    logger = ProcessingLogger(conn)

    register_source = RegisterSourceUseCase(source_repo)
    list_sources = ListSourcesUseCase(source_repo)
    import_uc = ImportSourceItemsUseCase(MockParser(), import_repo, item_repo, logger)
    search_uc = SearchCatalogUseCase(item_repo)
    theme_uc = AssignThemeUseCase(theme_repo)

    st.title("Catálogo Unificado de Acervo — Bootstrap")

    with st.expander("Cadastrar fonte"):
        name = st.text_input("Nome da fonte")
        source_type = st.text_input("Tipo", value="biblioteca_digital")
        parser_name = st.text_input("Parser", value="mock_csv")
        if st.button("Salvar fonte"):
            register_source.execute(name=name, source_type=source_type, parser_name=parser_name)
            st.success("Fonte cadastrada")

    sources = list_sources.execute()
    st.subheader("Fontes cadastradas")
    st.write([s.model_dump() for s in sources])

    with st.expander("Importar CSV mock"):
        source_id = st.number_input("Source ID", min_value=1, step=1)
        file_path = st.text_input("Caminho do CSV", value="data/samples/mock_source.csv")
        if st.button("Importar"):
            job_id = import_uc.execute(source_id=int(source_id), file_path=Path(file_path))
            st.success(f"Importação concluída. job_id={job_id}")

    st.subheader("Busca")
    query = st.text_input("Buscar (FTS5)", value="teologia")
    if st.button("Buscar"):
        result = search_uc.execute(query)
        st.write([item.model_dump() for item in result])

    with st.expander("Temas"):
        theme_name = st.text_input("Novo tema", value="Teologia")
        if st.button("Criar tema"):
            theme_id = theme_uc.create_theme(theme_name)
            st.success(f"Tema criado. id={theme_id}")
        st.write([t.model_dump() for t in theme_uc.list_themes()])


if __name__ == "__main__":
    main()
