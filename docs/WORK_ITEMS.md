# WORK_ITEMS.md

**Última atualização**: 2026-04-02

---

## Itens de trabalho

| ID | Tarefa | Status | Branch | Responsável |
|---|---|---|---|---|
| WI-001 | DTOs e mappers | ✅ done | main | Concluído |
| WI-002 | Integrar matching ao pipeline | ✅ done | main | Trabalhador 1 |
| WI-003 | Atualização seletiva por fonte | ✅ done | main | Trabalhador 2 |
| WI-004 | Revisão manual na UI | 📋 todo | — | Aguardando |
| WI-005 | Core hardening: matching canônico, skip materializado, gates, busca segura e UI | ✅ done | main | ChatGPT |
| WI-006 | Governança: tornar manutenibilidade critério explícito para agentes | ✅ done | main | ChatGPT |
| WI-007 | Parser Logos bootstrap: formato real, documentação e fixtures | ✅ done | main | ChatGPT |
| WI-008 | Housekeeping pós-merge: saneamento Git + reconciliação documental | 🚧 in_progress | assistant/repo-housekeeping | OpenCode |

---

## Histórico

| ID | Data | Commit | Status |
|---|---|---|---|
| WI-008 | 2026-04-02 | trabalho em progresso | 🚧 Auditoria pós-merge em execução para reconciliar estado real do Git e da documentação |
| WI-007 | 2026-04-02 | 2bed35a | ✅ Merge PR #6 em `main` com parser real `logos_csv`, documentação de formato e fixtures |
| WI-006 | 2026-04-01 | a73963d | ✅ Governança atualizada para exigir manutenibilidade junto com testabilidade |
| WI-005 | 2026-04-01 | 8fac35c | ✅ Core hardening mergeado em main |
| WI-001 | 2026-04-01 | f62e375 | ✅ Concluído |
| WI-002 | 2026-04-01 | 40f71ce | ✅ Concluído (merge em main) |
| WI-003 | 2026-04-01 | 0e885ee | ✅ Concluído (merge em main) |

---

## Worktrees Ativas

| Branch | Worktree | Escopo | Status |
|---|---|---|---|
| assistant/repo-housekeeping | C:/workspace/tmp/gestao-acervo | saneamento pós-merge: auditoria de branches, reconciliação documental e validação operacional | em execução |

---

## Próximos Passos

- WI-004: Revisão manual na UI
- Concluir WI-008 e validar merge sem regressão documental
- Estratégia de identidade estável para fontes sem ID confiável
- Próximo parser real depois da validação do Logos
