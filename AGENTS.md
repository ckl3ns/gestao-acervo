# AGENTS.md

## Visão rápida do projeto
Este projeto implementa um **catálogo unificado de acervo digital e físico**.
O sistema deve consolidar fontes heterogêneas, normalizar metadados, aplicar aliases, suportar atualização seletiva, gerar candidatos de matching e permitir revisão manual.

## Estado atual
O repositório já possui:
- app Streamlit mínima;
- SQLite com FTS5;
- ingestão por parser;
- pipeline novo de importação por fonte;
- aliases no pipeline;
- workflow inicial documentado.

O repositório ainda **não** concluiu:
- atualização seletiva real por fonte;
- integração operacional de matching;
- UI de revisão manual;
- trilha de auditoria madura.

Para os critérios verificáveis de saída do bootstrap, consulte `docs/MATURITY_CRITERIA.md`.

## Arquitetura resumida
- `app/`: interface Streamlit
- `src/catalogo_acervo/application`: casos de uso
- `src/catalogo_acervo/domain`: entidades, contratos e serviços
- `src/catalogo_acervo/infrastructure`: banco, repositórios, ingestão e logging
- `tests/`: testes unitários e de integração
- `docs/`: governança, arquitetura, decisões e status

## Ferramentas e comandos principais
Instalação:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Instalar hooks:
```bash
make install-hooks
```

Testes:
```bash
pytest -q
```

Rodar app:
```bash
streamlit run app/streamlit_app.py
```

## Modo de trabalho esperado do agente
1. ler `INSTRUCTIONS.md`;
2. ler `docs/STATUS.md` e `docs/WORK_ITEMS.md`;
3. escolher ou receber uma tarefa delimitada;
4. abrir branch/worktree isolada;
5. executar mudança pequena;
6. rodar testes;
7. checar se a mudança continua legível e fácil de manter;
8. registrar progresso;
9. commitar;
10. repetir.

## O que não fazer
- não alterar `main` diretamente;
- não fazer commits grandes e misturados;
- não ignorar testes falhando;
- não aumentar complexidade acidental sem necessidade;
- não pular atualização dos arquivos de status;
- não puxar escopo para IA/MCP/deploy antes do núcleo;
- não gerar documentação ornamental.

## Fonte de verdade para contexto operacional
Considere estes arquivos como fonte de verdade:
- `INSTRUCTIONS.md`
- `docs/STATUS.md`
- `docs/WORK_ITEMS.md`
- `docs/workflow.md`
- `docs/architecture.md`
- `docs/decisions.md`
- `docs/MATURITY_CRITERIA.md`
