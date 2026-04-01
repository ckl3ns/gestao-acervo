# STATUS.md

**Última atualização**: 2026-04-01  
**Projeto**: Catálogo Unificado de Acervo  
**Modelo operacional**: PO humano + Scrum Master/Tech Lead por agente + equipe de agentes em worktrees isoladas

---

## Estado atual do produto

### ✅ Concluído e funcional
- Bootstrap local-first com SQLite + FTS5
- App Streamlit mínima com `@st.cache_resource`
- Cadastro de fontes, importação por fonte com resolução de parser
- Aliases no pipeline de importação
- Upsert null-safe com COALESCE
- source_key com extração segura e fallback determinístico
- MatchScore + ConfidenceBand value objects
- Infraestrutura de dev: ruff, mypy, pytest-cov, pre-commit, pre-push
- conftest.py com fixtures compartilhadas
- **52 testes passando** (validado em 2026-04-01)

### 🚧 Próximas prioridades
1. **DTOs e mappers** — desacoplar Streamlit do domínio
2. **Matching operacional** — integrar suggest_matches ao pipeline
3. **Atualização seletiva** — merge strategy por campo
4. **Revisão manual na UI** — workflow de reconciliação

### ⚠️ Riscos conhecidos
- `interfaces/dto` e `interfaces/mappers` vazios — Streamlit acessa entidades diretamente
- `suggest_matches` use case existe mas não é chamado pelo pipeline
- mypy configurado mas não enforçado em hooks
- Parser mock é o único disponível (sem parser real CSV/JSON)

---

## Histórico recente

| Data | Commit | Entrega |
|---|---|---|
| 2026-04-01 | cb20120 | fix(app): corrigir SuggestMatchesUseCase e adicionar testes de MatchRepository |
| 2026-03-30 | 69ec452 | chore: V0 — bootstrap integrado com infra agentica |

---

## Critério de prioridade

**Foco atual**: integridade do núcleo, não estética ou IA.

1. DTOs/mappers para desacoplamento
2. Matching integrado ao pipeline
3. Atualização seletiva por fonte
4. Revisão manual
5. Só depois: IA, MCP, deploy
