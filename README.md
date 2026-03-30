# Catálogo Unificado de Acervo — Bootstrap

Bootstrap inicial local-first do projeto definido no PRD.

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Inicialização do banco

O banco é inicializado automaticamente ao abrir a aplicação Streamlit, ou manualmente com:

```bash
python -m catalogo_acervo.infrastructure.db.bootstrap
```

## Rodar aplicação

```bash
streamlit run app/streamlit_app.py
```

## Rodar testes

```bash
pytest
```

## Fluxo mínimo disponível

1. Cadastrar fonte.
2. Importar CSV mock (`data/samples/mock_source.csv`).
3. Buscar itens pelo campo normalizado com FTS5.
4. Criar e listar temas.

## Estrutura

- `app/`: interface Streamlit.
- `src/catalogo_acervo/application`: casos de uso.
- `src/catalogo_acervo/domain`: entidades/serviços/contratos.
- `src/catalogo_acervo/infrastructure`: DB, repositórios, ingestão, logging.
- `tests/`: unitários e integração.
