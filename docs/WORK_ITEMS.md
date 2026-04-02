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
| WI-007 | Parser Logos bootstrap: formato real, documentação e fixtures | ✅ ready_for_pr | assistant/logos-parser-bootstrap | ChatGPT |

---

## Histórico

| ID | Data | Commit | Status |
|---|---|---|---|
| WI-007 | 2026-04-02 | preparação local/branch | ✅ Parser real `logos_csv` preparado com documentação do formato, fixtures pequenas e smoke test de matching |
| WI-006 | 2026-04-01 | a73963d | ✅ Governança atualizada para exigir manutenibilidade junto com testabilidade |
| WI-005 | 2026-04-01 | 8fac35c | ✅ Core hardening mergeado em main |
| WI-001 | 2026-04-01 | f62e375 | ✅ Concluído |
| WI-002 | 2026-04-01 | 40f71ce | ✅ Concluído (merge em main) |
| WI-003 | 2026-04-01 | 0e885ee | ✅ Concluído (merge em main) |

---

## Worktrees Ativas

| Branch | Worktree | Escopo | Status |
|---|---|---|---|
| assistant/logos-parser-bootstrap | n/a (preparação por branch + pacote local) | parser Logos 7/10, documentação de formato, fixtures reais, overlap para matching e wiring mínimo no app/testes | pronta para PR |

---

## Próximos Passos

- WI-004: Revisão manual na UI
- Executar a suíte completa após aplicar o pacote desta entrega
- Estratégia de identidade estável para fontes sem ID confiável
- Próximo parser real depois da validação do Logos
