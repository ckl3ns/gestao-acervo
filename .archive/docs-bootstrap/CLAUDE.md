# CLAUDE.md — Catálogo Unificado de Acervo

> Este arquivo é lido pelo Claude Code a **cada turno de conversa**.
> Use `@./caminho/para/arquivo.md` para incluir referências externas inline.

---

## 1. IDENTIDADE DO PROJETO

**Nome:** Catálogo Unificado de Acervo Digital e Físico  
**Versão:** V0 (bootstrap local-first)  
**Objetivo:** Consolidar fontes heterogêneas (Logos, Accordance, PDFs, OneDrive), normalizar metadados, busca consolidada, matching entre fontes e revisão manual.  
**Stack:** Python 3.10+ · SQLite + FTS5 · Pydantic v2 · RapidFuzz · Streamlit · Pytest  
**Modelo operacional:** PO humano (Cristian) + agentes Claude Code em worktrees isoladas

---

## 2. SETUP OBRIGATÓRIO

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make install-hooks
make quality          # deve passar: lint + 48 testes verdes
```

Se `make quality` falhar, **pare aqui** e resolva antes de qualquer coisa.

---

## 3. COMANDOS DO DIA A DIA

| Objetivo | Comando |
|---|---|
| Testes rápidos | `python -m pytest -q` |
| Lint | `python -m ruff check src/ tests/ app/` |
| Auto-fix lint | `python -m ruff check src/ tests/ app/ --fix` |
| Testes + cobertura | `make coverage` |
| Lint + testes | `make quality` |
| App Streamlit | `make run` |
| Instalar hooks | `make install-hooks` |

**Threshold de cobertura:** 70% mínimo (enforced no pre-push hook).

---

## 4. MAPA DE ARQUIVOS

### Interface (UI apenas — zero lógica de negócio)
```
app/streamlit_app.py
  _get_db_connection()   → @st.cache_resource — conexão única por processo
  _build_use_cases(conn) → composição de todas as dependências
  main()                 → renderização Streamlit
```

### Aplicação (orquestração — zero lógica de domínio)
```
src/catalogo_acervo/application/use_cases/
  import_source_items_from_source.py  ← TRILHA CANÔNICA (única entrada de importação)
    _extract_source_key()             → extração segura: source_key → id → auto:{sid}:{i}
  register_source.py      → cadastra fonte com parser_name
  list_sources.py         → lista fontes
  search_catalog.py       → FTS5
  assign_theme.py         → cria/associa temas
  suggest_matches.py      → sugere matches ⚠️ desconectado do pipeline (WI-003)
```

### Domínio (lógica pura — zero dependência de infra)
```
src/catalogo_acervo/domain/
  entities/
    catalog_item.py     → CatalogItem (Pydantic)
    source.py           → Source
    alias.py            → Alias
    import_job.py       → ImportJob
    match.py, manual_review.py, theme.py, item_theme.py, processing_log.py
  services/
    normalization.py    → normalize_text()  — NFKD + lowercase + strip
    aliasing.py         → apply_aliases()   — com source_scope
    matching.py         → suggest_match()   — retorna MatchScore (value object)
    theming.py          → slugify_theme()   — remove diacríticos
  value_objects/
    match_score.py      → MatchScore + ConfidenceBand (frozen Pydantic, validado)
  contracts/
    parser_contract.py  → ParserContract (Protocol — structural typing)
```

### Infraestrutura
```
src/catalogo_acervo/infrastructure/
  db/
    schema.sql                       → schema completo com triggers FTS5
    connection.py                    → get_connection() + init_db()
    repositories/
      catalog_item_repository.py     → upsert null-safe com COALESCE ⚠️
      source_repository.py
      source_lookup_repository.py
      alias_repository.py
      import_repository.py
      match_repository.py            → (WI-003: pouco coberto ainda)
      theme_repository.py
  ingestion/
    base_parser.py       → BaseParser (implementa ParserContract)
    parser_registry.py   → ParserRegistry — dict[str, ParserContract]
    parsers/mock_parser.py → parser_name="mock_csv"
  logging/
    processing_logger.py → ProcessingLogger — persiste em processing_logs
```

### Testes
```
tests/
  conftest.py               → db_conn (SQLite :memory:) + 8 fixtures
  unit/
    test_normalization.py
    test_aliasing.py
    test_mock_parser.py
    test_parser_registry.py
    test_source_key_extraction.py    → _extract_source_key() 7 casos
    test_match_score.py              → MatchScore + ConfidenceBand 13 casos
    test_catalog_item_repository.py  → upsert null-safe 8 casos
    test_use_cases_basic.py          → ListSources + AssignTheme 6 casos
  integration/
    test_import_and_search.py
    test_import_from_source_pipeline.py  → + FTS5 sync test
```

### Governança e infra agentica
```
.claude/
  settings.json              → permissões configuradas (sem click fatigue)
  rules/                     → regras modulares por domínio (lidas a cada turno)
  agents/                    → subagentes especializados por WI
  commands/                  → slash commands customizados
  session-memory/config/template.md → template de session memory customizado
CLAUDE.md                    → este arquivo (lido a cada turno)
CLAUDE.local.md              → notas privadas do PO (gitignored)
```

---

## 5. TRILHA CANÔNICA DE IMPORTAÇÃO

```
RegisterSourceUseCase.execute(name, source_type, parser_name)
      ↓ salva fonte com parser_name
ImportSourceItemsFromSourceUseCase.execute(source_id, file_path)
      ↓ busca source → resolve parser via ParserRegistry.get(parser_name)
      ↓ _extract_source_key(record, source_id, index)
        prioridade: record["source_key"] → record["id"] → "auto:{sid}:{i}"
      ↓ apply_aliases(field, alias_kind, aliases, source_scope=parser_name)
      ↓ CatalogItemRepository.upsert(item)
        ON CONFLICT: COALESCE campos opcionais (null-safe merge)
        triggers FTS5 sincronizam automaticamente
      ↓ ImportRepository.finish(job_id, status, totals)
      ↓ ProcessingLogger.log(...)

NUNCA usar ImportSourceItemsUseCase — foi removido. Arquivo não existe.
SEMPRE registrar a fonte antes de importar (FK constraint).
```

---

## 6. ANTI-PADRÕES CONHECIDOS

### A. FK constraint em testes unitários
```python
# ERRADO
item_repo.upsert(CatalogItem(source_id=1, ...))  # → IntegrityError

# CERTO — fixture registered_source_id do conftest
def test_algo(item_repo, registered_source_id):
    item_repo.upsert(CatalogItem(source_id=registered_source_id, ...))
```

### B. Conexão SQLite sem cache no Streamlit
```python
# ERRADO — nova conexão a cada rerender (vaza recursos)
def main():
    conn = get_connection(settings.db_path)

# CERTO
@st.cache_resource
def _get_db_connection():
    return get_connection(settings.db_path)
```

### C. source_key derivado do título
```python
# ERRADO — None vira "None", títulos iguais colidem no UNIQUE
source_key = str(record.get("source_key") or record.get("title"))

# CERTO — _extract_source_key() no use case
source_key = _extract_source_key(record, source_id, index)
```

### D. Upsert que apaga campos com NULL
```sql
-- ERRADO — reimportação sem year apaga year existente
ON CONFLICT DO UPDATE SET year = excluded.year

-- CERTO
ON CONFLICT DO UPDATE SET year = COALESCE(excluded.year, year)
```

### E. slugify sem diacríticos
```python
# ERRADO — "Bíblica" → "bíblica" no slug
slug = "-".join(name.lower().split())

# CERTO — usar slugify_theme()
from catalogo_acervo.domain.services.theming import slugify_theme
slug = slugify_theme("Teologia Bíblica")  # → "teologia-biblica"
```

### F. Setup duplicado em testes
```python
# ERRADO — 20 linhas de setup por teste
def test_algo(tmp_path):
    conn = get_connection(tmp_path / "test.db")
    init_db(conn, schema_path)
    repo = SourceRepository(conn)
    ...

# CERTO — conftest cobre tudo
def test_algo(db_conn, source_repo, item_repo):
    ...
```

---

## 7. CONVENÇÕES DE CÓDIGO

- `from __future__ import annotations` em todo arquivo de domínio.
- Nunca importar `sqlite3` no domínio.
- Nunca importar `streamlit` fora de `app/`.
- Type hints completos em toda função nova.
- `Protocol` para contracts (não ABC).
- `model_config = {"frozen": True}` em value objects.
- Arquivo ideal: 200–400 linhas. Máximo absoluto: 600.
- Imports ordenados automaticamente pelo ruff.

---

## 8. REGRAS DE BANCO

- Toda mudança de schema = migration com rollback.
- FTS5 sincronizado por triggers — nunca atualizar `catalog_items_fts` diretamente.
- `PRAGMA foreign_keys = ON` em toda conexão.
- `conn.commit()` imediatamente após cada write.
- Campos com COALESCE: title_norm, author_*, series_*, publisher_*, year, language, volume, edition, path_or_location, resource_type.
- Campos sempre sobrescritos: title_raw, item_type, raw_record_json, is_active, current_import_id, updated_at.

---

## 9. REGRAS DE TESTES

- Todo comportamento novo = teste novo. Sem exceção.
- Casos de borda > caminho feliz.
- Nunca usar `tmp_path` para banco (usar `db_conn` do conftest).
- Nunca `time.sleep()` em testes.
- Nunca mockar o banco — testar contra SQLite in-memory.
- Nunca commitar com testes falhando.
- Nunca commitar com ruff reportando erros.

---

## 10. REGRAS DE AGENTE

### Antes de qualquer trabalho
1. Este arquivo (`CLAUDE.md`) — já lido.
2. `docs/STATUS.md` — estado atual.
3. `docs/WORK_ITEMS.md` — backlog e handoffs.
4. `make quality` — confirmar baseline verde.

### Durante
- Uma tarefa = uma worktree = uma branch.
- Commits semânticos: `feat(*)`, `fix(*)`, `test(*)`, `docs(*)`, `chore(*)`, `refactor(*)`.
- `make quality` antes de cada commit.
- Atualizar `docs/STATUS.md` e `docs/WORK_ITEMS.md` ao concluir.

### Proibições absolutas
- Nunca alterar `main` diretamente.
- Nunca commitar com ruff ou testes falhando.
- Nunca criar UI sofisticada antes do núcleo consistente.
- Nunca introduzir LLM, embeddings, MCP operacional nesta fase.

---

## 11. CRIAR NOVA WORKTREE

```bash
git worktree add ../wt-<tema> -b assistant/<tema>
cd ../wt-<tema>
pip install -e ".[dev]"
make install-hooks
# ... trabalhe ... make quality antes de cada commit ...
cd /projeto-original
git worktree remove ../wt-<tema>
```

Formatos de branch: `assistant/<tema>` | `codex/<tema>` | `agent/<tema>`

---

## 12. PRIORIDADE DO BACKLOG

```
[CRÍTICO] WI-002: Atualização seletiva por fonte
          MergePolicy enum + campo em sources + upsert(item, policy)
          Fundação pronta: COALESCE já no repositório.

[ALTA]    WI-003: Matching integrado ao pipeline
          suggest_match() existe mas não é chamado em nenhum ponto.

[ALTA]    WI-004: Revisão manual na UI (depende WI-003)

[MÉDIA]   WI-005: DTOs e mappers (interfaces/ ainda vazio)

[MÉDIA]   WI-006: Parsers reais (Logos, Accordance, PDFs)

[BAIXA]   WI-007: mypy no CI (configurado, não enforced)
```

---

## 13. DIÁRIO DE ERROS (aprendizados do codebase)

| # | Erro | Causa | Solução |
|---|---|---|---|
| 1 | `IntegrityError: FOREIGN KEY` em unit tests | source_id sem fonte cadastrada | Fixture `registered_source_id` no conftest |
| 2 | FTS5 com duplicatas após reimportação | Trigger sincronizava apenas INSERT | Teste `test_fts5_stays_in_sync_after_upsert_conflict` |
| 3 | `source_key = "None"` para itens sem título | `str(None)` vira `"None"` | `_extract_source_key()` com fallback determinístico |
| 4 | Slug com diacríticos | `slugify_theme` não normalizava | NFKD + combining chars + regex |
| 5 | Reimportação apagava `year` | `SET year = excluded.year` | `COALESCE(excluded.year, year)` |
| 6 | Nova conexão SQLite a cada rerender | `main()` recriava conexão | `@st.cache_resource` |

---

## 14. COMO O CLAUDE CODE LÊ ESTE ARQUIVO

O Claude Code carrega a seguinte hierarquia a **cada turno**:
```
1. /etc/claude-code/CLAUDE.md        → managed (corporativo)
2. ~/.claude/CLAUDE.md               → usuário global
3. ~/.claude/rules/*.md              → regras globais do usuário
4. CLAUDE.md  ou  .claude/CLAUDE.md  → projeto (este arquivo)
5. .claude/rules/*.md                → regras modulares do projeto
6. CLAUDE.local.md                   → privado do PO (gitignored)
```

Prioridade: arquivos posteriores sobrescrevem anteriores.  
Arquivos mais próximos do diretório atual têm prioridade mais alta.  
`@./path/to/file.md` dentro de qualquer arquivo inclui outro arquivo inline.

**`CLAUDE.local.md`** (gitignored): use para notas de PO, credenciais locais, prioridades temporárias que não devem aparecer no histórico público.

**Session memory**: o Claude Code mantém automaticamente `~/.claude/projects/{hash}/{sessionId}/session-memory/summary.md` com contexto estruturado. Template customizado em `.claude/session-memory/config/template.md`.  
Use `/compact` antes de mudanças de contexto grandes.  
Use `claude --continue` para retomar sessões com contexto acumulado.

---

## 15. REFERÊNCIAS

- PRD: `gestao-acervo-prd.md`
- Arquitetura: `docs/architecture.md`  
- ADRs: `docs/decisions.md`
- Status: `docs/STATUS.md`
- Backlog: `docs/WORK_ITEMS.md`
- Workflow de branches: `docs/workflow.md`
- Modelo de roteamento completo: `docs/model-routing.md`
