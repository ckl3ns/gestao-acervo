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
- **DTOs e mappers** — CatalogItemDTO, SourceDTO, mappers bidirecionais (WI-001)
- **Matching integrado ao pipeline** — suggest_matches chamado após upsert (WI-002)
- **MergePolicy enum (REPLACE, MERGE, KEEP_EXISTING)** — upsert com merge_policy (WI-003)
- source_key com extração segura e fallback determinístico
- MatchScore + ConfidenceBand value objects
- Infraestrutura de dev: ruff, mypy, pytest-cov, pre-commit, pre-push
- conftest.py com fixtures compartilhadas
- **58 testes passando, 75% cobertura** (validado em 2026-04-01)

### 🚧 Próximas prioridades
1. **Revisão manual na UI** — workflow de reconciliação (WI-004)
2. **Parser real CSV/JSON** — substituir MockParser
3. **Auditoria** — trilha de decisões de reconciliação

### ⚠️ Riscos conhecidos
- DTOs/mappers criados mas não usados na UI ainda
- mypy configurado mas não enforçado em hooks
- Parser mock é o único disponível

---

## Histórico recente

| Data | Commit | Entrega |
|---|---|---|
| 2026-04-01 | a994daf | merge: WI-003 concluído (MergePolicy) |
| 2026-04-01 | 40f71ce | feat(matching): integrar suggest_matches ao pipeline (WI-002) |
| 2026-04-01 | f62e375 | feat(interfaces): DTOs e mappers (WI-001) |
| 2026-04-01 | 0e885ee | feat(upsert): adicionar merge policy por campo (WI-003) |

---

## Critério de prioridade

**Foco atual**: integridade do núcleo, não estética ou IA.

1. DTOs/mappers para desacoplamento
2. Matching integrado ao pipeline
3. Atualização seletiva por fonte
4. Revisão manual
5. Só depois: IA, MCP, deploy
