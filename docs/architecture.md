# Arquitetura do Bootstrap (v2)

## Camadas

1. **Interface (`app/`)**: Streamlit para operações mínimas de cadastro, importação, busca e administração básica.
2. **Interfaces (`interfaces/`)**: DTOs e mappers para desacoplar UI das entidades de domínio.
3. **Aplicação (`application/use_cases/`)**: orquestra casos de uso (`register_source`, `import_source_items_from_source`, `search_catalog`, `suggest_matches`, `assign_theme`).
4. **Domínio (`domain/`)**: entidades, value objects, serviços de normalização/matching e contratos (incluindo parser contract).
5. **Persistência (`infrastructure/db/`)**: conexão SQLite, schema, repositórios e FTS5.
6. **Ingestão (`infrastructure/ingestion/`)**: `ParserRegistry`, parser base, `mock_csv` e parser real `logos_csv`.

## Decisões vigentes

- Local-first com SQLite + FTS5.
- Pipeline de importação orientado por `source_id` e `parser_name`, com aliases e upsert por política de merge.
- Matching incremental acionado após importação para reduzir custo de recomputação global.
- Parser real já incorporado (`logos_csv`) sem remover o parser mock de suporte a testes e cenários sintéticos.
