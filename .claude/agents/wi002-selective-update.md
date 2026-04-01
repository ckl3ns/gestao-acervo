# Agente: WI-002 — Atualização Seletiva por Fonte

> Subagente especializado para implementar WI-002.
> Ler CLAUDE.md e docs/WORK_ITEMS.md antes de iniciar.

## Role

Engenheiro de software sênior responsável por implementar atualização seletiva por fonte no pipeline de importação.

## Contexto

A fundação já está pronta: `CatalogItemRepository.upsert()` usa `COALESCE` para campos opcionais.

O que **ainda falta**:
1. `MergePolicy` enum com três estratégias
2. Campo `merge_policy` na tabela `sources`
3. Migration SQL correspondente
4. `upsert(item, policy=MergePolicy.KEEP_EXISTING)` no repositório
5. `ImportSourceItemsFromSourceUseCase` passando a policy da fonte
6. Testes cobrindo cada policy

## Invariantes obrigatórios

- Nunca alterar `schema.sql` sem criar arquivo de migration em `migrations/`.
- Nunca commitar sem `make quality` verde.
- Atualizar `docs/STATUS.md` e `docs/WORK_ITEMS.md` ao finalizar.
- Registrar handoff completo (ver template em `.claude/rules/05-agent-workflow.md`).

## Especificação técnica

### MergePolicy enum

```python
# src/catalogo_acervo/domain/value_objects/merge_policy.py
from enum import Enum

class MergePolicy(str, Enum):
    ALWAYS_OVERWRITE = "always_overwrite"
    # Sempre sobrescreve todos os campos (comportamento pré-COALESCE)
    
    KEEP_EXISTING = "keep_existing"
    # COALESCE: preserva campo existente se novo for NULL (comportamento atual padrão)
    
    PREFER_NEWER = "prefer_newer"
    # Sobrescreve apenas se o novo valor não for NULL E o import_id for mais recente
```

### Migration SQL

```sql
-- migrations/YYYYMMDD_add_merge_policy_to_sources.sql
ALTER TABLE sources ADD COLUMN merge_policy TEXT NOT NULL DEFAULT 'keep_existing';
```

### Assinatura do upsert

```python
def upsert(self, item: CatalogItem, policy: MergePolicy = MergePolicy.KEEP_EXISTING) -> int:
    ...
```

## Testes mínimos obrigatórios

1. `test_merge_policy_always_overwrite_replaces_null_with_null` — campo year: 2020 → None
2. `test_merge_policy_keep_existing_preserves_year_when_new_is_none` — field: 2020, novo: None → 2020
3. `test_merge_policy_prefer_newer_updates_when_newer_import` — import_id maior → atualiza
4. `test_source_merge_policy_persisted_and_loaded` — round-trip pelo banco
5. `test_import_pipeline_uses_source_merge_policy` — teste de integração

## Branch e worktree

```bash
git worktree add ../wt-WI002-merge-policy -b assistant/WI002-merge-policy
```
