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

## O que este bootstrap entrega — e o que ele não prova

Este repositório é um **bootstrap funcional**: a espinha dorsal arquitetural está
implementada e o loop de desenvolvimento funciona.

**O que está entregue:**
- Estrutura de domínio (entidades, value objects, contratos)
- Pipeline de importação com parser, aliases e upsert com merge policy
- Matching gerado e persistido após importação
- DTOs e mappers para desacoplamento UI ↔ domínio
- Infraestrutura de dev (testes, hooks, cobertura)

**O que ainda não foi provado:**
- Identidade de item sob reimportações com dados reais
- Matching funcionando sob crescimento real de acervo
- Revisão humana fechando o ciclo de reconciliação
- Ingestão real sem implodir premissas do domínio

Para os critérios verificáveis de saída do bootstrap, consulte
[docs/MATURITY_CRITERIA.md](docs/MATURITY_CRITERIA.md).

## Estrutura

- `app/`: interface Streamlit.
- `src/catalogo_acervo/application`: casos de uso.
- `src/catalogo_acervo/domain`: entidades/serviços/contratos.
- `src/catalogo_acervo/infrastructure`: DB, repositórios, ingestão, logging.
- `tests/`: unitários e integração.

## Workflow de colaboração

A governança operacional do repositório está distribuída nestes arquivos:
- `INSTRUCTIONS.md`: regras obrigatórias para agentes;
- `AGENTS.md`: contexto operacional resumido do projeto;
- `docs/STATUS.md`: estado atual, prioridades e riscos;
- `docs/WORK_ITEMS.md`: quadro de trabalho e handoffs;
- `docs/workflow.md`: fluxo detalhado de branches, commits e PRs.

Todo agente deve ler esses arquivos antes de iniciar uma tarefa.
Esse workflow define:
- branch por tarefa;
- commits semânticos e pequenos;
- handoff por ZIP quando o conector não fechar o ciclo de edição;
- checklist de PR e de revisão;
- ordem de ataque do backlog para evitar dispersão em UI/IA/deploy cedo demais.
