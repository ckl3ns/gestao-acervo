# Catálogo Unificado de Acervo

Sistema local-first para consolidar, normalizar e reconciliar acervos digitais e físicos de múltiplas fontes heterogêneas.

## O que faz

- Ingere itens de múltiplas fontes via parsers plugáveis
- Normaliza metadados e aplica aliases configuráveis
- Persiste com upsert seletivo por fonte (merge policy por campo)
- Gera candidatos de matching entre itens de fontes diferentes
- Permite busca full-text com SQLite FTS5
- Expõe interface mínima via Streamlit para cadastro, importação e busca

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Uso

Inicializar banco (feito automaticamente pelo Streamlit, ou manualmente):

```bash
python -m catalogo_acervo.infrastructure.db.bootstrap
```

Rodar aplicação:

```bash
streamlit run app/streamlit_app.py
```

Rodar testes:

```bash
pytest
```

## Estrutura

```
src/catalogo_acervo/
  domain/          # entidades, value objects, contratos, serviços
  application/     # casos de uso
  infrastructure/  # banco, repositórios, ingestão, logging
  interfaces/      # DTOs e mappers
app/               # interface Streamlit
tests/             # unitários e integração
docs/              # arquitetura, decisões, status, workflow
```

## Estágio atual

Este repositório é um **bootstrap funcional**: espinha dorsal arquitetural implementada, loop de desenvolvimento funcionando, caminho crítico com dados reais ainda não provado.

Consulte [`docs/STATUS.md`](docs/STATUS.md) para o estado atual e [`docs/MATURITY_CRITERIA.md`](docs/MATURITY_CRITERIA.md) para os critérios de saída do bootstrap.

## Documentação

| Arquivo | Conteúdo |
|---|---|
| [`INSTRUCTIONS.md`](INSTRUCTIONS.md) | Regras obrigatórias para agentes |
| [`docs/STATUS.md`](docs/STATUS.md) | Estado atual, prioridades e riscos |
| [`docs/WORK_ITEMS.md`](docs/WORK_ITEMS.md) | Backlog e handoffs |
| [`docs/MATURITY_CRITERIA.md`](docs/MATURITY_CRITERIA.md) | Critérios de saída do bootstrap |
| [`docs/architecture.md`](docs/architecture.md) | Decisões arquiteturais |
| [`docs/workflow.md`](docs/workflow.md) | Fluxo de branches, commits e PRs |
