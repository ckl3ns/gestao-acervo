# Arquitetura do Bootstrap (v1)

## Camadas

1. **Interface (`app/`)**: Streamlit para operações mínimas de cadastro, importação e busca.
2. **Aplicação (`application/use_cases/`)**: orquestra casos de uso sem conhecer detalhes de UI.
3. **Domínio (`domain/`)**: entidades, serviços de normalização/matching/temas e contrato de parser.
4. **Persistência (`infrastructure/db/`)**: conexão SQLite, schema e repositórios.
5. **Ingestão (`infrastructure/ingestion/`)**: parser base e parser mock CSV.

## Decisões

- Local-first com SQLite + FTS5.
- Entidades refletindo o modelo conceitual mínimo do PRD.
- Importação seletiva por fonte via caso de uso `ImportSourceItemsUseCase`.
- Parser real ainda não implementado; parser mock garante trilha funcional inicial.
