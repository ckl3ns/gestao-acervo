# STATUS.md

## Resumo executivo
Projeto: **Catálogo Unificado de Acervo**
Modelo operacional: **PO humano + Scrum Master/Tech Lead por agente + equipe de agentes em worktrees isoladas**

---

## Estado atual do produto

### Concluído
- Bootstrap local-first com SQLite + FTS5
- App Streamlit mínima com `@st.cache_resource` (conexão não recriada por rerender)
- Cadastro de fontes, importação por fonte com resolução de parser
- Aliases no pipeline de importação
- Testes unitários e de integração (42 passando)
- Workflow inicial de colaboração
- Governança multiagente com hooks e instruções
- **Upsert null-safe com COALESCE** (campos opcionais preservados em reimportação parcial)
- **source_key com extração segura e fallback determinístico** (sem colisão por título)
- **MatchScore + ConfidenceBand value objects** (score tipado, imutável, com validação)
- **Remoção do use case legado** (trilha canônica única)
- **Infraestrutura de dev**: ruff, mypy, pytest-cov, pre-commit lint, pre-push cobertura
- **conftest.py**: fixtures compartilhadas para testes (sem setup duplicado)
- **CLAUDE.md**: arquivo de bootstrap para Claude Code

### Em andamento / próximo alvo
- WI-002: Atualização seletiva real por fonte (fundação COALESCE entregue neste PR)

### Ainda não concluído
- Matching operacional integrado ao fluxo principal (WI-003)
- Revisão manual na UI (WI-004)
- Auditoria mais forte de decisões de reconciliação
- Relatórios operacionais mínimos
- DTOs e mappers em `interfaces/` (pastas criadas, vazias)

---

## Últimas entregas relevantes

| Data | Branch | Commit | Status | Entrega |
|---|---|---|---|---|
| 2026-03-30 | assistant/review-app-integration | 3510780 | concluído | app conectado ao pipeline novo e aliases na UI |
| 2026-03-30 | assistant/governance-agent-operating-model | e4bf033 | concluído | hooks para bloquear commit sem testes |
| 2026-03-30 | assistant/governance-agent-operating-model | a24cde5 | concluído | workflow multiagente com worktrees |
| 2026-03-30 | assistant/infra-maturidade-dev | a2298ff | concluído | ruff, mypy, pytest-cov configurados |
| 2026-03-30 | assistant/infra-maturidade-dev | 74e84a2 | concluído | hooks: lint no pre-commit, cobertura no pre-push |
| 2026-03-30 | assistant/infra-maturidade-dev | 73fda02 | concluído | conftest.py + teste FTS5 upsert sync |
| 2026-03-30 | assistant/infra-maturidade-dev | 76db3f4 | concluído | removido use case legado (trilha única) |
| 2026-03-30 | assistant/infra-maturidade-dev | f777c9a | concluído | source_key null-safe + 7 testes |
| 2026-03-30 | assistant/infra-maturidade-dev | 966cdd9 | concluído | MatchScore + ConfidenceBand value objects |
| 2026-03-30 | assistant/infra-maturidade-dev | 8243405 | concluído | upsert null-safe COALESCE + 8 testes |
| 2026-03-30 | assistant/infra-maturidade-dev | d3c7b40 | concluído | fix Streamlit connection cache |

---

## Critério de prioridade
A prioridade atual **não é** estética do app nem integração de IA.
A prioridade atual é **integridade do núcleo**:

1. Atualização seletiva completa por fonte (WI-002)
2. Matching integrado ao pipeline (WI-003)
3. Revisão manual (WI-004)
4. Auditoria
5. Só depois: IA, MCP, deploy

---

## Riscos ativos
- WI-002 ainda não tem branch aberta nem responsável designado
- `interfaces/dto` e `interfaces/mappers` vazios — sem DTOs, o Streamlit acessa entidades diretamente
- Sem `mypy --strict` sendo executado no CI por agora (configurado mas não no hook)
- `suggest_matches` use case existe mas não é chamado pelo pipeline de importação

---

## Regra de atualização deste arquivo
Atualizar sempre que:
- Uma grande tarefa começar ou terminar
- A prioridade do backlog mudar
- Surgir risco estrutural novo
