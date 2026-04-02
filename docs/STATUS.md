# STATUS.md

**Última atualização**: 2026-04-01 (core-hardening + governança de manutenibilidade concluídos em branch de trabalho)  
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
- Aliases no pipeline de importação - **com precedência correta (específico > global)**
- Upsert null-safe com COALESCE - **retornando inserted/updated/skipped**
- **DTOs e mappers** - CatalogItemDTO, SourceDTO, mappers bidirecionais (WI-001)
- **Matching integrado ao pipeline** - suggest_matches chamado após upsert, incremental por affected_ids (WI-002)
- **MergePolicy enum (REPLACE, MERGE, KEEP_EXISTING)** - upsert com merge_policy (WI-003)
- source_key com extração segura e **fallback por hash SHA-256 determinístico**
- MatchScore + ConfidenceBand value objects
- **Matching canônico e idempotente** - pares persistidos como `(min_id, max_id)` e contagem `created` só sobe quando houve inserção real
- **ImportJob com contadores reais** - inserted/updated/skipped/errors separados
- **Proteção de falha no parser** - job finalizado como `failed` em caso de exceção
- **Busca FTS5 sanitizada** - queries de usuário, inclusive tokens com hífen, não causam `OperationalError`
- **Validação precoce de parser** no cadastro da fonte
- **UI principal alinhada ao núcleo atual** - import usa `SuggestMatchesUseCase` e exibe DTOs/mappers
- Infraestrutura de dev: ruff, mypy, pytest-cov, pre-commit, pre-push
- Dependências dev reproduzíveis com `hypothesis` incluído em `.[dev]`
- Fixtures compartilhadas com fechamento explícito de conexão SQLite
- **109 testes passando** com cobertura total em **79%**

### 🚧 Próximas prioridades
1. **Revisão manual na UI** - workflow de reconciliação (WI-004)
2. **Parser real CSV/JSON** - substituir MockParser
3. **Identidade estável além do fallback por hash** - evitar tratar alteração de conteúdo como novo item quando a fonte não fornece ID estável
4. **Auditoria operacional mínima** - trilha legível para decisões de matching e revisão manual
5. **Usar DTOs/mappers de forma mais ampla na interface**

### ⚠️ Riscos conhecidos
- Parser mock ainda é o único parser disponível
- Fallback por hash continua sendo estratégia de emergência, não identidade estável longitudinal
- Caminho crítico com dados reais não provado - ver [docs/MATURITY_CRITERIA.md](docs/MATURITY_CRITERIA.md)
- Cobertura total aceitável não elimina áreas ainda sem exercício relevante (manual_review, match entity, processing_log entity)
- Linguagem de "funcional" não implica "operacionalmente confiável"

---

## Histórico recente

| Data | Commit | Entrega |
|---|---|---|
| 2026-04-01 | em preparação | fix(core): matching canônico, skip materializado, busca FTS5 segura e governança de manutenibilidade |
| 2026-04-01 | a994daf | merge: WI-003 concluído (MergePolicy) |
| 2026-04-01 | 40f71ce | feat(matching): integrar suggest_matches ao pipeline (WI-002) |
| 2026-04-01 | f62e375 | feat(interfaces): DTOs e mappers (WI-001) |
| 2026-04-01 | 0e885ee | feat(upsert): adicionar merge policy por campo (WI-003) |

---

## Critério de prioridade

**Foco atual**: integridade do núcleo, não estética ou IA.

1. identidade estável e atualização seletiva confiável
2. matching + revisão manual
3. auditoria operacional mínima
4. parsers reais
5. só depois: IA, MCP, deploy
