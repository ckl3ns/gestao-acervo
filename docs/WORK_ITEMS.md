# WORK_ITEMS.md

Este arquivo controla o trabalho ativo e o handoff entre agentes.

## Legenda de status
- `todo`
- `in_progress`
- `blocked`
- `done`
- `handoff`

---

## Itens de trabalho

| ID | Tarefa | Status | Prioridade | Branch | Modelo principal | Responsável | Último commit | Testes | Próximo passo |
|---|---|---|---|---|---|---|---|---|---|
| WI-001 | Governança multiagente, hooks, instruções, status, workflow | done | alta | assistant/governance-agent-operating-model | ChatGPT (sem registro) | ChatGPT | a24cde5 | `pytest -q` ✓ | merge em main |
| WI-INF | Maturidade de infra dev: ruff, conftest, null-safe, value objects, CLAUDE.md | done | alta | assistant/infra-maturidade-dev | Claude Sonnet | Claude | d3c7b40 | 42 passando ✓ | PR + merge |
| WI-002 | Atualização seletiva real por fonte (merge strategy por campo) | todo | crítica | _a definir_ | _a definir_ | _a definir_ | — | — | abrir worktree; definir MergePolicy enum; implementar field-level override |
| WI-003 | Matching operacional integrado ao pipeline | todo | alta | _a definir_ | _a definir_ | _a definir_ | — | — | depende de WI-002 |
| WI-004 | Revisão manual na UI | todo | alta | _a definir_ | _a definir_ | _a definir_ | — | — | depende de WI-003 |

---

## Template de handoff

```markdown
### Handoff <ID>
- data:
- branch:
- worktree:
- responsável atual:
- modelo principal:
- fallback:
- tarefa:
- status:
- commits:
- testes executados:
- arquivos alterados:
- riscos conhecidos:
- próximo passo:
```

---

## Regras de atualização deste arquivo
Atualizar sempre que:
- Uma worktree for criada
- Um item passar para `in_progress`, `blocked`, `handoff` ou `done`
- Houver troca de responsável
- Houver mudança relevante de branch, commit ou próximos passos
- Modelo principal utilizado for registrado (campo obrigatório para rastreabilidade)

---

### Handoff WI-001
- data: 2026-03-30
- branch: assistant/governance-agent-operating-model
- worktree: ../wt-governance-agent-operating-model
- responsável atual: ChatGPT
- modelo principal: não registrado
- fallback: não registrado
- tarefa: governança multiagente e disciplina operacional do repositório
- status: done
- commits: e4bf033, 5f2a96e, 752e2fc, a24cde5
- testes executados: `pytest -q` após cada commit
- arquivos alterados: `.githooks/pre-commit`, `scripts/install-hooks.sh`, `Makefile`, `INSTRUCTIONS.md`, `AGENTS.md`, `docs/STATUS.md`, `docs/WORK_ITEMS.md`, `docs/workflow.md`, `README.md`
- riscos conhecidos: agentes podem ignorar atualização de status
- próximo passo: merge em main

### Handoff WI-INF
- data: 2026-03-30
- branch: assistant/infra-maturidade-dev
- worktree: (executado em clone de análise, sem worktree separada)
- responsável atual: Claude Sonnet
- modelo principal: claude-sonnet-4-6
- fallback: —
- tarefa: rodada de maturidade de infraestrutura de desenvolvimento agentico
- status: done — pronto para PR
- commits: a2298ff, 74e84a2, 73fda02, 76db3f4, f777c9a, 966cdd9, 8243405, d3c7b40, (este)
- testes executados: `pytest -q` após cada commit; 42 passando ao final
- arquivos alterados: pyproject.toml, Makefile, .githooks/pre-commit, .githooks/pre-push (novo),
  tests/conftest.py (novo), tests/unit/test_source_key_extraction.py (novo),
  tests/unit/test_match_score.py (novo), tests/unit/test_catalog_item_repository.py (novo),
  tests/integration/* (refatorados), src/*/value_objects/match_score.py (novo),
  src/*/domain/services/matching.py (atualizado), src/*/repositories/catalog_item_repository.py
  (null-safe upsert + get_by_source_and_key), app/streamlit_app.py (cache_resource),
  CLAUDE.md (novo), docs/STATUS.md, docs/WORK_ITEMS.md
- riscos conhecidos:
  - `interfaces/dto` e `interfaces/mappers` ainda vazios
  - mypy não roda no hook (está configurado mas não enforced automaticamente)
  - WI-002 não tem responsável nem branch
- próximo passo: abrir WI-002 com branch e definir MergePolicy
