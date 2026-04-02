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
data/
  imports/logos/raw/   # exports reais locais do Logos (não comitáveis)
  samples/             # fixtures pequenas comitáveis para testes
tests/             # unitários e integração
docs/              # arquitetura, decisões, status, workflow e formatos
```

## Logos: primeira camada de parser real

O repositório passa a ter uma primeira camada de parser real para exportações CSV do Logos:

- parser: `logos_csv`
- formatos observados: Logos 7 e Logos 10
- documentação do layout: [`docs/formats/logos_csv.md`](docs/formats/logos_csv.md)
- exemplos pequenos para regressão:
  - `data/samples/logos10_sample.csv`
  - `data/samples/logos7_sample.csv`
  - `data/samples/logos10_matching_sample.csv`
  - `data/samples/logos7_matching_sample.csv`

Exports reais de trabalho devem ficar em `data/imports/logos/raw/`. Consulte
[`data/imports/logos/raw/README.md`](data/imports/logos/raw/README.md).

## Estágio atual

Este repositório continua sendo um **bootstrap funcional**: a espinha dorsal arquitetural existe, mas o caminho crítico com dados reais ainda está em validação progressiva.

A diferença agora é concreta: já existe um parser real para uma fonte real, com documentação do formato e fixtures derivadas de arquivos reais.

Consulte [`docs/STATUS.md`](docs/STATUS.md) para o estado atual e [`docs/MATURITY_CRITERIA.md`](docs/MATURITY_CRITERIA.md) para os critérios de saída do bootstrap.

## Documentação

| Arquivo | Conteúdo |
|---|---|
| [`INSTRUCTIONS.md`](INSTRUCTIONS.md) | Regras obrigatórias para agentes |
| [`AGENTS.md`](AGENTS.md) | Contexto operacional resumido do projeto |
| [`docs/prd.md`](docs/prd.md) | PRD — visão de produto, requisitos e roadmap |
| [`docs/STATUS.md`](docs/STATUS.md) | Estado atual, prioridades e riscos |
| [`docs/WORK_ITEMS.md`](docs/WORK_ITEMS.md) | Backlog e handoffs |
| [`docs/MATURITY_CRITERIA.md`](docs/MATURITY_CRITERIA.md) | Critérios de saída do bootstrap |
| [`docs/architecture.md`](docs/architecture.md) | Decisões arquiteturais |
| [`docs/decisions.md`](docs/decisions.md) | ADRs |
| [`docs/workflow.md`](docs/workflow.md) | Fluxo de branches, commits e PRs |
| [`docs/conformidade.md`](docs/conformidade.md) | Snapshot de conformidade e observações de governança |
| [`docs/formats/logos_csv.md`](docs/formats/logos_csv.md) | Estrutura observada dos CSVs Logos 7 e 10 |
