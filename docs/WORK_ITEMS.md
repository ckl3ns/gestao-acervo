# WORK_ITEMS.md

**Última atualização**: 2026-04-01

Este arquivo controla o trabalho ativo e o handoff entre agentes.

## Legenda de status
- `todo` — não iniciado
- `in_progress` — em execução
- `blocked` — impedido
- `done` — concluído

---

## Itens de trabalho ativos

| ID | Tarefa | Status | Prioridade | Responsável | Próximo passo |
|---|---|---|---|---|---|
| WI-001 | DTOs e mappers básicos | todo | crítica | _a designar_ | criar DTOs para CatalogItem, Source, Theme; implementar mappers bidirecionais |
| WI-002 | Integrar matching ao pipeline de importação | todo | alta | _a designar_ | chamar suggest_matches após upsert; persistir candidatos |
| WI-003 | Atualização seletiva por fonte | todo | alta | _a designar_ | definir MergePolicy enum; implementar field-level override |
| WI-004 | Revisão manual na UI | todo | média | _a designar_ | depende de WI-002 |

---

## Regras de atualização
Atualizar sempre que:
- Uma worktree for criada
- Um item mudar de status
- Houver troca de responsável
- Houver mudança relevante de próximos passos
