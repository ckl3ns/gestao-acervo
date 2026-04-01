# WORK_ITEMS.md

**Última atualização**: 2026-04-01

---

## Itens de trabalho

| ID | Tarefa | Status | Branch | Responsável |
|---|---|---|---|---|
| WI-001 | DTOs e mappers | ✅ done | main | Concluído |
| WI-002 | Integrar matching ao pipeline | ✅ done | main | Trabalhador 1 |
| WI-003 | Atualização seletiva por fonte | ✅ done | main | Trabalhador 2 |
| WI-004 | Revisão manual na UI | 📋 todo | — | Aguardando |
| WI-005 | Core hardening: matching canônico, skip materializado, gates e UI | ✅ done | assistant/core-hardening | ChatGPT |

---

## Histórico

| ID | Data | Commit | Status |
|---|---|---|---|
| WI-005 | 2026-04-01 | em preparação | ✅ Implementado localmente; branch/PR pendentes de publicação |
| WI-001 | 2026-04-01 | f62e375 | ✅ Concluído |
| WI-002 | 2026-04-01 | 40f71ce | ✅ Concluído (merge em main) |
| WI-003 | 2026-04-01 | 0e885ee | ✅ Concluído (merge em main) |

---

## Worktrees Ativas

| Branch | Worktree | Escopo | Status |
|---|---|---|---|
| assistant/core-hardening | n/a (execução local via snapshot do repositório) | matching canônico, contagem honesta, skip materializado, gates e wiring | pronta para PR |

---

## Próximos Passos

- WI-004: Revisão manual na UI
- Parser real CSV/JSON
- Estratégia de identidade estável para fontes sem ID confiável
