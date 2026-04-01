# Regras: Convenções de Banco de Dados

> Carregado automaticamente pelo Claude Code a cada turno.

## Conexão

```python
# Sempre via get_connection() — nunca sqlite3.connect() diretamente
from catalogo_acervo.infrastructure.db.connection import get_connection, init_db

conn = get_connection(db_path)     # aplica row_factory + foreign_keys ON
init_db(conn, schema_path)         # aplica schema.sql idempotente
```

**`PRAGMA foreign_keys = ON`** obrigatório — `get_connection()` já faz isso, mas nunca criar conexão bypassing essa função.

## Schema

- Toda mudança de schema = arquivo de migration com rollback explícito.
- Naming: `migrations/YYYYMMDD_HHMMSS_<descricao>.sql`
- Nunca renomear colunas existentes sem migration.
- FTS5 é sincronizado por triggers — **nunca atualizar `catalog_items_fts` diretamente**.

## Upsert null-safe (regra crítica)

```sql
-- Campos SEMPRE sobrescritos em ON CONFLICT:
--   title_raw, item_type, raw_record_json, is_active,
--   current_import_id, updated_at

-- Campos com COALESCE (preserva existente se novo for NULL):
--   title_norm, subtitle_raw,
--   author_raw, author_norm,
--   series_raw, series_norm,
--   publisher_raw, publisher_norm,
--   year, language, volume, edition,
--   path_or_location, resource_type

-- ERRADO:
ON CONFLICT DO UPDATE SET year = excluded.year

-- CERTO:
ON CONFLICT DO UPDATE SET year = COALESCE(excluded.year, year)
```

**Por quê:** uma reimportação parcial (sem o campo `year`, por exemplo) não deve apagar dados válidos de importações anteriores mais completas.

## FTS5

```python
# Query FTS5 — sempre com parâmetros posicionais
rows = conn.execute(
    """
    SELECT c.*
    FROM catalog_items_fts f
    JOIN catalog_items c ON c.id = f.rowid
    WHERE catalog_items_fts MATCH ?
    ORDER BY rank
    """,
    (query,),
).fetchall()
```

- FTS5 MATCH aceita: `word`, `"exact phrase"`, `column:value`, `word*` (prefix).
- Não usar `f-strings` em queries SQL — SQL injection risk.
- Testar FTS5 explicitamente após upsert com conflito (ver `test_fts5_stays_in_sync_after_upsert_conflict`).

## Repositórios

- Todo repositório recebe `conn: sqlite3.Connection` no `__init__`.
- `conn.commit()` imediatamente após cada write operation.
- Nunca usar `SELECT *` — usar `SELECT * FROM` só em `_to_entity()` onde `dict(row)` é o ponto de entrada.
- Método `_to_entity(row: sqlite3.Row) -> Entity` deve ser `@staticmethod`.

## Transações

- Operações em múltiplas tabelas = transação explícita:
  ```python
  try:
      conn.execute("BEGIN")
      conn.execute("INSERT INTO ...")
      conn.execute("UPDATE ...")
      conn.commit()
  except Exception:
      conn.rollback()
      raise
  ```

## Proibições

- Nunca usar `sqlite3` diretamente no domínio ou application.
- Nunca atualizar `catalog_items_fts` fora dos triggers.
- Nunca commitar schema.sql sem testar `init_db()` em banco limpo.
- Nunca usar `raw_record_json` como `TEXT` — sempre `json.dumps()` / `json.loads()`.
