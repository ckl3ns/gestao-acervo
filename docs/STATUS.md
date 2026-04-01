# STATUS.md

**Última atualização**: 2026-04-01 (core-integrity-fixes em andamento)  
**Projeto**: Catálogo Unificado de Acervo  
**Modelo operacional**: PO humano + Scrum Master/Tech Lead por agente + equipe de agentes em worktrees isoladas

---

## Estado atual do produto

### ✅ Concluído e funcional no bootstrap

> Os itens abaixo estão implementados e testados no contexto do bootstrap local-first.
> Nenhum deles foi validado com dados reais em escala operacional.
> Consulte [docs/MATURITY_CRITERIA.md](docs/MATURITY_CRITERIA.md) para os critérios de saída do bootstrap.

- Bootstrap local-first com SQLite + FTS5
- App Streamlit mínima com `@st.cache_resource`
- Cadastro de fontes, importação por fonte com resolução de parser
- Aliases no pipeline de importação — **com precedência correta (específico > global)**
- Upsert null-safe com COALESCE — **retornando inserted/updated/skipped**
- **DTOs e mappers** — CatalogItemDTO, SourceDTO, mappers bidirecionais (WI-001)
- **Matching integrado ao pipeline** — suggest_matches chamado após upsert, incremental por affected_ids (WI-002)
- **MergePolicy enum (REPLACE, MERGE, KEEP_EXISTING)** — upsert com merge_policy (WI-003)
- source_key com extração segura e **fallback por hash SHA-256 determinístico**
- MatchScore + ConfidenceBand value objects
- **Tabela matches com UNIQUE(left_item_id, right_item_id)** — matching idempotente
- **ImportJob com contadores reais** — inserted/updated/skipped/errors separados
- **Proteção de falha no parser** — job finalizado como "failed" em caso de exceção
- **Busca FTS5 sanitizada** — queries de usuário não causam OperationalError
- Infraestrutura de dev: ruff, mypy, pytest-cov, pre-commit, pre-push
- conftest.py com fixtures compartilhadas
- **104 testes passando** (58 originais + 46 novos de core-integrity-fixes)

### 🚧 Próximas prioridades
1. **Wiring do matching na UI** — task 9 da spec core-integrity-fixes
2. **Corrigir erros mypy** — tasks 11–12
3. **Habilitar mypy no pre-push** — task 13
4. **Revisão manual na UI** — workflow de reconciliação (WI-004)
5. **Parser real CSV/JSON** — substituir MockParser

### ⚠️ Riscos conhecidos
- DTOs/mappers criados mas não usados na UI ainda
- mypy configurado mas não enforçado em hooks (tasks 11–13 pendentes)
- Parser mock é o único disponível
- Wiring do matching na UI pendente (task 9)
- Caminho crítico com dados reais não provado — ver [docs/MATURITY_CRITERIA.md](docs/MATURITY_CRITERIA.md)
- Linguagem de "funcional" não implica "operacionalmente confiável"

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
