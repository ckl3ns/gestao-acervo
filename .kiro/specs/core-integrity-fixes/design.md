# Design — core-integrity-fixes

## Overview

Este documento descreve as mudanças técnicas concretas para corrigir 8 falhas estruturais identificadas no núcleo do sistema de catálogo unificado. As correções cobrem semântica de importação, idempotência de matching, estabilidade de identidade de objetos, proteção de falhas no parser, precedência de aliases, sanitização FTS5, wiring da UI e governança de qualidade de código.

Todas as mudanças são cirúrgicas: cada correção toca o menor conjunto possível de arquivos e não altera contratos públicos além do necessário.

---

## Architecture

O sistema segue arquitetura em camadas (domain → application → infrastructure → interfaces). As correções respeitam essa separação:

```
┌─────────────────────────────────────────────────────┐
│  app/streamlit_app.py  (Req 7: wiring)              │
├─────────────────────────────────────────────────────┤
│  application/use_cases/                             │
│    import_source_items_from_source.py  (Req 1,3,4) │
│    suggest_matches.py                  (Req 2)      │
│    search_catalog.py                   (Req 6)      │
├─────────────────────────────────────────────────────┤
│  domain/                                            │
│    entities/import_job.py              (Req 1)      │
│    services/aliasing.py                (Req 5)      │
├─────────────────────────────────────────────────────┤
│  infrastructure/                                    │
│    db/schema.sql                       (Req 2)      │
│    db/repositories/import_repository.py (Req 1)    │
│    db/repositories/catalog_item_repository.py (Req 1)│
│    db/repositories/alias_repository.py (Req 5)     │
│    db/repositories/match_repository.py (Req 2)     │
├─────────────────────────────────────────────────────┤
│  pyproject.toml / .githooks/           (Req 8)      │
└─────────────────────────────────────────────────────┘
```

Não há novos componentes arquiteturais. Todas as correções são modificações internas a componentes existentes.

---

## Components and Interfaces

### Req 1 — Semântica Verdadeira de Importação

**`domain/entities/import_job.py`**

Mudança: `import_mode` default de `"full_replace"` para `"upsert"`.

```python
class ImportJob(BaseModel):
    import_mode: str = "upsert"   # era "full_replace"
```

**`infrastructure/db/repositories/catalog_item_repository.py`**

`upsert()` precisa retornar um literal indicando se foi INSERT ou UPDATE. O SQLite não expõe isso diretamente via `lastrowid` em conflito, mas `cursor.rowcount` retorna `1` para INSERT e `1` para UPDATE via `ON CONFLICT DO UPDATE`. A distinção real é feita via `changes()` comparado com `last_insert_rowid()`: se `last_insert_rowid()` mudou, foi INSERT; caso contrário, UPDATE.

Estratégia: antes do upsert, verificar existência com `SELECT id`. Isso é O(1) por chave indexada `UNIQUE(source_id, source_key)`.

```python
def upsert(self, item: CatalogItem, merge_policy: MergePolicy = MergePolicy.MERGE) -> tuple[int, str]:
    """Retorna (item_id, operation) onde operation é 'inserted' | 'updated' | 'skipped'."""
    existing = self.conn.execute(
        "SELECT id, raw_record_json FROM catalog_items WHERE source_id = ? AND source_key = ?",
        (item.source_id, item.source_key),
    ).fetchone()

    new_json = json.dumps(item.raw_record_json, ensure_ascii=False, sort_keys=True)

    if existing and existing["raw_record_json"] == new_json:
        # Conteúdo idêntico — skip
        return int(existing["id"]), "skipped"

    # ... executa INSERT ON CONFLICT DO UPDATE ...
    operation = "updated" if existing else "inserted"
    return item_id, operation
```

**`infrastructure/db/repositories/import_repository.py`**

`finish()` recebe `total_updated` e `total_skipped`:

```python
def finish(
    self,
    job_id: int,
    status: str,
    total_read: int,
    total_inserted: int,
    total_updated: int,
    total_skipped: int,
    total_errors: int,
) -> None:
    self.conn.execute(
        """
        UPDATE imports
        SET status = ?, total_read = ?, total_inserted = ?,
            total_updated = ?, total_skipped = ?, total_errors = ?
        WHERE id = ?
        """,
        (status, total_read, total_inserted, total_updated, total_skipped, total_errors, job_id),
    )
    self.conn.commit()
```

**`application/use_cases/import_source_items_from_source.py`**

Pipeline separa contadores:

```python
inserted = updated = skipped = errors = 0

for index, record in enumerate(records):
    try:
        ...
        item_id, operation = self.item_repository.upsert(item)
        if operation == "inserted":
            inserted += 1
        elif operation == "updated":
            updated += 1
        else:
            skipped += 1
    except Exception as exc:
        errors += 1
        ...

self.import_repository.finish(
    job_id, status, len(records), inserted, updated, skipped, errors
)
```

---

### Req 2 — Idempotência e Unicidade de Matching

**`infrastructure/db/schema.sql`**

Adicionar constraint na tabela `matches`:

```sql
CREATE TABLE IF NOT EXISTS matches (
  ...
  UNIQUE(left_item_id, right_item_id),   -- NOVO
  FOREIGN KEY (left_item_id) REFERENCES catalog_items(id),
  FOREIGN KEY (right_item_id) REFERENCES catalog_items(id)
);
```

Para bancos existentes, será necessária uma migration ou `DROP TABLE` + recreate no bootstrap.

**`infrastructure/db/repositories/match_repository.py`**

Trocar `INSERT` por `INSERT OR IGNORE`:

```python
def add(self, left_item_id: int, right_item_id: int, score: float, rule: str, status: str, confidence_band: str) -> int:
    cursor = self.conn.execute(
        """
        INSERT OR IGNORE INTO matches
            (left_item_id, right_item_id, match_score, match_rule, status, confidence_band)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (left_item_id, right_item_id, score, rule, status, confidence_band),
    )
    self.conn.commit()
    return int(cursor.lastrowid or 0)
```

**`application/use_cases/suggest_matches.py`**

`execute()` recebe lista opcional de `affected_item_ids` para evitar varredura O(n²) total:

```python
def execute(self, threshold: float = 85.0, affected_item_ids: list[int] | None = None) -> int:
    items = self.items_repo.list_all()
    if affected_item_ids is not None:
        affected_set = set(affected_item_ids)
        candidates = [i for i in items if i.id in affected_set]
    else:
        candidates = items

    created = 0
    for left in candidates:
        for right in items:
            if left.id == right.id or left.source_id == right.source_id:
                continue
            match_result = suggest_match(left, right)
            if match_result.score >= threshold:
                self.match_repo.add(
                    left.id or 0, right.id or 0,
                    match_result.score, match_result.rule,
                    "possible", match_result.band.value,
                )
                created += 1
    return created
```

O pipeline passa os IDs dos itens inseridos/atualizados:

```python
# em ImportSourceItemsFromSourceUseCase.execute()
affected_ids: list[int] = []
# ... no loop: affected_ids.append(item_id)
if self.suggest_matches_use_case is not None:
    self.suggest_matches_use_case.execute(affected_item_ids=affected_ids)
```

---

### Req 3 — Fallback de source_key por Hash

**`application/use_cases/import_source_items_from_source.py`**

Substituir `_extract_source_key()`:

```python
import hashlib
import json as _json

def _extract_source_key(record: dict, source_id: int, index: int) -> str:
    for field in _SOURCE_KEY_CANDIDATES:
        value = record.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()

    # Fallback: hash SHA-256 truncado do conteúdo do registro (order-independent)
    content = _json.dumps(record, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"hash:{digest}"
```

O parâmetro `index` é mantido na assinatura para compatibilidade mas não é mais usado no fallback. O logger registra quando o fallback é acionado (ver Req 4 — o mesmo bloco de logging do pipeline cobre isso).

---

### Req 4 — Proteção de Falha no Parser

**`application/use_cases/import_source_items_from_source.py`**

Envolver `parser.parse()` em try/except com finalização garantida:

```python
def execute(self, source_id: int, file_path: Path) -> int:
    source = self.source_lookup.get_by_id(source_id)
    if source is None:
        raise ValueError(f"Fonte {source_id} não encontrada")

    parser = self.parser_registry.get(source.parser_name)
    aliases = self.alias_lookup.list_active()

    job_id = self.import_repository.create(
        ImportJob(source_id=source_id, status="running", raw_file_name=file_path.name)
    )

    try:
        records = parser.parse(file_path)
    except Exception as exc:
        self.logger.log(
            message="Falha no parser — importação abortada",
            level="ERROR",
            source_id=source_id,
            import_id=job_id,
            context={"parser_name": source.parser_name, "file_path": str(file_path), "error": str(exc)},
        )
        self.import_repository.finish(job_id, "failed", 0, 0, 0, 0, 1)
        raise

    # ... resto do pipeline ...
```

A garantia de "nenhum job fica running" é satisfeita porque:
1. Falha no parser → `finish("failed")` + re-raise
2. Falha no loop de registros → erros acumulados, `finish("completed_with_errors")`
3. Sucesso → `finish("completed")`

---

### Req 5 — Precedência de Aliases por Especificidade

**`infrastructure/db/repositories/alias_repository.py`**

Mudar `ORDER BY` em `list_active()`:

```python
def list_active(self) -> list[Alias]:
    rows = self.conn.execute(
        """
        SELECT * FROM aliases
        WHERE is_active = 1
        ORDER BY
            CASE WHEN source_scope IS NULL THEN 1 ELSE 0 END,
            alias_kind,
            alias_text
        """
    ).fetchall()
    return [Alias.model_validate(dict(row)) for row in rows]
```

Aliases com `source_scope` não-nulo aparecem primeiro. O `apply_aliases()` existente já para na primeira correspondência (`return normalize_text(alias.canonical_text)`), então a ordem da lista determina a precedência. Nenhuma mudança necessária em `aliasing.py`.

---

### Req 6 — Sanitização de Queries FTS5

**`application/use_cases/search_catalog.py`**

Adicionar função de sanitização e aplicá-la antes de passar ao repositório:

```python
import re

def _sanitize_fts5_query(query: str) -> str:
    """Remove tokens que causam OperationalError no SQLite FTS5.

    Estratégia conservadora: remove caracteres problemáticos e operadores
    isolados, preservando palavras válidas.
    """
    if not query or not query.strip():
        return ""

    # Remove aspas não fechadas
    if query.count('"') % 2 != 0:
        query = query.replace('"', '')

    # Remove parênteses não balanceados
    open_count = query.count('(')
    close_count = query.count(')')
    if open_count != close_count:
        query = query.replace('(', '').replace(')', '')

    # Remove operadores FTS5 isolados (AND, OR, NOT no início/fim ou sozinhos)
    query = re.sub(r'\b(AND|OR|NOT)\s*$', '', query, flags=re.IGNORECASE)
    query = re.sub(r'^\s*(AND|OR|NOT)\b', '', query, flags=re.IGNORECASE)

    # Remove ^ e * isolados (sem palavra adjacente)
    query = re.sub(r'(?<!\w)[\^*]|[\^*](?!\w)', '', query)

    return query.strip()


class SearchCatalogUseCase:
    def __init__(self, repository: CatalogItemRepository) -> None:
        self.repository = repository

    def execute(self, query: str) -> list[CatalogItem]:
        sanitized = _sanitize_fts5_query(query)
        if not sanitized:
            return []
        return self.repository.search(sanitized)
```

---

### Req 7 — Wiring do Matching na UI

**`app/streamlit_app.py`**

Importar `SuggestMatchesUseCase` e `MatchRepository`, instanciar e passar para `ImportSourceItemsFromSourceUseCase`:

```python
from catalogo_acervo.application.use_cases.suggest_matches import SuggestMatchesUseCase
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository

def _build_use_cases(conn):
    ...
    match_repo = MatchRepository(conn)
    suggest_matches_uc = SuggestMatchesUseCase(
        items_repo=item_repo,
        match_repo=match_repo,
    )
    import_uc = ImportSourceItemsFromSourceUseCase(
        source_lookup=source_lookup,
        alias_lookup=alias_repo,
        parser_registry=parser_registry,
        import_repository=import_repo,
        item_repository=item_repo,
        logger=logger,
        suggest_matches_use_case=suggest_matches_uc,   # NOVO
    )
    ...
```

---

### Req 8 — Mypy e Cobertura

**Erros mypy a corrigir:**

Os 10 erros típicos são:
- `dict` sem type args → `dict[str, Any]` ou `dict[str, str]`
- `int | None` sem conversão segura → usar `int(x) if x is not None else default`
- Funções sem anotação de retorno → adicionar `-> None`, `-> int`, etc.

Arquivos afetados (a confirmar com `mypy src`):
- `infrastructure/db/repositories/*.py` — `dict` sem args em SQL params
- `application/use_cases/import_source_items_from_source.py` — `record: dict` sem args
- `domain/entities/*.py` — campos `int | None` sem guard

**`pyproject.toml`** — configuração mypy:

```toml
[tool.mypy]
strict = false
disallow_untyped_defs = true
```

**`.githooks/pre-push`** — adicionar mypy:

```bash
#!/bin/sh
set -e
python -m mypy src
python -m pytest -q
```

---

## Data Models

Nenhum novo modelo de dados. Mudanças nos modelos existentes:

| Entidade | Campo | Mudança |
|---|---|---|
| `ImportJob` | `import_mode` | default `"full_replace"` → `"upsert"` |
| `imports` (tabela) | — | `finish()` agora persiste `total_updated` e `total_skipped` (colunas já existem no schema) |
| `matches` (tabela) | — | nova constraint `UNIQUE(left_item_id, right_item_id)` |

O schema já possui as colunas `total_updated` e `total_skipped` na tabela `imports`. A única mudança de schema é a constraint UNIQUE na tabela `matches`.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invariante de conservação de contadores

*For any* importação concluída (com ou sem erros), a soma `total_inserted + total_updated + total_skipped + total_errors` deve ser igual a `total_read`.

**Validates: Requirements 1.7**

---

### Property 2: Corretude do contador de upsert

*For any* registro processado pelo pipeline, se o par `(source_id, source_key)` já existia no banco antes do upsert, o contador `total_updated` deve ser incrementado; se não existia, `total_inserted` deve ser incrementado; se o conteúdo era idêntico, `total_skipped` deve ser incrementado.

**Validates: Requirements 1.2, 1.3, 1.4**

---

### Property 3: Nenhum ImportJob permanece com status "running"

*For any* execução do método `execute()` do pipeline — seja bem-sucedida, com erros de registro ou com falha no parser — o `ImportJob` correspondente deve ter status diferente de `"running"` após o término do método.

**Validates: Requirements 4.1, 4.2, 4.4, 4.5**

---

### Property 4: Idempotência do matching

*For any* conjunto de dados no banco, executar `SuggestMatchesUseCase.execute()` duas vezes consecutivas sem alterar os dados deve resultar na mesma contagem de linhas na tabela `matches` antes e depois da segunda execução.

**Validates: Requirements 2.3, 2.4**

---

### Property 5: Deduplicação de pares de matching

*For any* par `(left_item_id, right_item_id)`, inserir o mesmo par duas vezes via `MatchRepository.add()` não deve criar linha duplicada na tabela `matches` e não deve lançar exceção.

**Validates: Requirements 2.1, 2.2**

---

### Property 6: Determinismo do source_key de fallback

*For any* registro sem campo `source_key` ou `id`, o `source_key` gerado pelo fallback deve ser idêntico independentemente da posição do registro no arquivo ou da ordem de processamento entre execuções distintas.

**Validates: Requirements 3.1, 3.2, 3.3**

---

### Property 7: Precedência de alias específico sobre global

*For any* conjunto de aliases contendo um alias com `source_scope` não-nulo e um alias global com o mesmo `alias_text` e `alias_kind`, `apply_aliases()` deve retornar o `canonical_text` do alias específico, independentemente da ordem de inserção no banco.

**Validates: Requirements 5.1, 5.2, 5.4, 5.5**

---

### Property 8: Segurança de sanitização FTS5

*For any* string de entrada (incluindo strings com parênteses não balanceados, aspas não fechadas, operadores FTS5 isolados, strings vazias e strings com apenas espaços), `SearchCatalogUseCase.execute()` não deve lançar `sqlite3.OperationalError`.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

---

## Error Handling

| Cenário | Comportamento atual | Comportamento corrigido |
|---|---|---|
| Parser lança exceção | Job fica `status="running"` para sempre | `finish("failed")` + re-raise |
| Registro sem título | Erro capturado, `total_errors++` | Sem mudança |
| Query FTS5 inválida | `sqlite3.OperationalError` propagado | Sanitização prévia, retorna `[]` |
| Par de match duplicado | `UNIQUE constraint failed` exception | `INSERT OR IGNORE`, sem exceção |
| Hash collision no source_key | Não tratado | Log de colisão + `total_errors++` |

---

## Testing Strategy

### Abordagem dual

Testes unitários cobrem exemplos específicos, casos de borda e condições de erro. Testes de propriedade cobrem invariantes universais com inputs gerados aleatoriamente. Ambos são necessários e complementares.

### Testes unitários (exemplos e casos de borda)

- `test_import_job_default_mode`: verifica que `ImportJob()` nasce com `import_mode="upsert"`
- `test_finish_persists_updated_skipped`: verifica que `finish()` persiste `total_updated` e `total_skipped`
- `test_parser_failure_sets_failed_status`: mock parser que lança, verifica status no banco
- `test_parser_failure_reraises`: verifica que a exceção é re-lançada após `finish()`
- `test_alias_scoped_wins_over_global`: alias específico e global para mesmo texto, verifica qual vence
- `test_fts5_empty_query_returns_empty`: query vazia retorna lista vazia
- `test_fts5_unbalanced_parens`: query `"(foo"` não lança exceção
- `test_match_duplicate_insert_ignored`: inserir mesmo par duas vezes, verificar count=1
- `test_suggest_matches_wired_in_app`: instanciar `_build_use_cases()` e verificar que `import_uc.suggest_matches_use_case` não é None
- `test_matching_integration_finds_similar_items`: dados com itens sabidamente similares, verifica count > 0 e par específico presente

### Testes de propriedade (property-based testing)

Biblioteca: **hypothesis** (já disponível no ecossistema Python, compatível com pytest).

Configuração mínima: `@settings(max_examples=100)` em cada teste de propriedade.

Tag format: `# Feature: core-integrity-fixes, Property N: <texto>`

```python
# Feature: core-integrity-fixes, Property 1: counter conservation invariant
@given(st.lists(st.text(min_size=1), min_size=0, max_size=20))
@settings(max_examples=100)
def test_counter_conservation(record_titles):
    # Gera registros, executa pipeline, verifica soma dos contadores == total_read
    ...

# Feature: core-integrity-fixes, Property 2: upsert counter correctness
@given(st.booleans())  # True = item já existe, False = novo
@settings(max_examples=100)
def test_upsert_counter_correctness(item_exists):
    ...

# Feature: core-integrity-fixes, Property 3: no job stays running
@given(st.booleans())  # True = parser falha, False = sucesso
@settings(max_examples=100)
def test_no_job_stays_running(parser_fails):
    ...

# Feature: core-integrity-fixes, Property 4: match idempotence
@given(st.lists(catalog_item_strategy(), min_size=2, max_size=10))
@settings(max_examples=100)
def test_match_idempotence(items):
    ...

# Feature: core-integrity-fixes, Property 5: match deduplication
@given(st.integers(min_value=1), st.integers(min_value=1))
@settings(max_examples=100)
def test_match_deduplication(left_id, right_id):
    ...

# Feature: core-integrity-fixes, Property 6: source_key determinism
@given(st.dictionaries(st.text(), st.text()))
@settings(max_examples=100)
def test_source_key_determinism(record):
    # Verifica que _extract_source_key produz mesmo resultado em qualquer ordem
    ...

# Feature: core-integrity-fixes, Property 7: alias scoped precedence
@given(st.text(min_size=1), st.text(min_size=1), st.text(min_size=1))
@settings(max_examples=100)
def test_alias_scoped_precedence(alias_text, global_canonical, scoped_canonical):
    ...

# Feature: core-integrity-fixes, Property 8: FTS5 sanitization safety
@given(st.text())
@settings(max_examples=200)
def test_fts5_never_raises(query):
    # Verifica que nenhuma string causa OperationalError
    ...
```

Cada propriedade é implementada por um único teste de propriedade. Testes de unidade cobrem os casos de borda específicos listados acima.

### Cobertura mínima

- `interfaces/dto` e `interfaces/mappers`: ≥ 80%
- `domain/entities/manual_review`, `domain/entities/match`, `infrastructure/logging/processing_log`: ≥ 80%
