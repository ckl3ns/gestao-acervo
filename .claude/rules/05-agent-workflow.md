# Regras: Workflow de Agente

> Carregado automaticamente pelo Claude Code a cada turno.

## Início obrigatório de toda sessão

```bash
# 1. Confirmar baseline verde
make quality

# 2. Verificar estado atual
cat docs/STATUS.md
cat docs/WORK_ITEMS.md

# 3. Identificar ou receber tarefa
# 4. Criar worktree isolada (para tarefas grandes)
git worktree add ../wt-<tema> -b assistant/<tema>
```

## Worktrees — padrão de isolamento

- Uma grande tarefa = uma branch = uma worktree.
- **Formato de branch:** `assistant/<tema>` | `codex/<tema>` | `agent/<tema>`
- **Nunca reutilizar** worktree para tarefa diferente.
- Remover worktree ao finalizar: `git worktree remove ../wt-<tema>`

```bash
# Criar
git worktree add ../wt-WI002-merge-policy -b assistant/WI002-merge-policy

# Trabalhar
cd ../wt-WI002-merge-policy
pip install -e ".[dev]"
make install-hooks

# Finalizar
cd /repo-original
git worktree remove ../wt-WI002-merge-policy
```

## Commits semânticos

```
feat(escopo): descrição      → nova funcionalidade
fix(escopo): descrição       → correção de bug
test(escopo): descrição      → testes novos ou corrigidos
refactor(escopo): descrição  → sem mudança de comportamento
docs(escopo): descrição      → documentação
chore(escopo): descrição     → tooling, config, deps
perf(escopo): descrição      → performance
```

**Exemplos do projeto:**
```bash
feat(domain): add MergePolicy enum with three strategies
fix(db): null-safe upsert with COALESCE for optional fields
test(infra): add conftest.py with shared in-memory DB fixtures
refactor(app): remove deprecated ImportSourceItemsUseCase
docs(governance): add CLAUDE.md; update STATUS and WORK_ITEMS
```

**Regras:**
- Um commit = uma mudança semanticamente isolada.
- Nunca misturar feat + refactor + docs no mesmo commit.
- `make quality` antes de cada commit.
- Commits pequenos e reversíveis.

## Definição de pronto (DoD)

Uma tarefa só está pronta quando:
- [ ] Branch própria com commits semânticos
- [ ] Testes verdes (`python -m pytest -q`)
- [ ] Lint limpo (`python -m ruff check`)
- [ ] Cobertura ≥ 70% (`make coverage`)
- [ ] `docs/STATUS.md` atualizado
- [ ] `docs/WORK_ITEMS.md` atualizado com handoff
- [ ] Sem risco estrutural escondido

## Template de handoff (WORK_ITEMS.md)

```markdown
### Handoff WI-XXX
- data: YYYY-MM-DD
- branch: assistant/<tema>
- worktree: ../wt-<tema>
- responsável atual: <agente>
- modelo principal: <modelo>
- fallback: <modelo ou —>
- tarefa: <descrição>
- status: done | in_progress | blocked
- commits: <sha1>, <sha2>, ...
- testes executados: `make quality` — N passando
- arquivos alterados: <lista>
- riscos conhecidos: <lista>
- próximo passo: <ação concreta>
```

## Uso de /compact e --continue

- **`/compact`**: usar proativamente antes de trocar de contexto (ex: passar de WI-002 para WI-003).
- **`claude --continue`**: sempre ao retomar sessão em andamento. Nunca abrir sessão nova quando existe worktree ativa.
- Session memory é acumulada automaticamente — não perder contexto por preguiça de usar `--continue`.

## Proibições absolutas

- Nunca alterar `main` diretamente.
- Nunca fazer merge de branch sem testes verdes.
- Nunca pular atualização de `docs/STATUS.md` e `docs/WORK_ITEMS.md`.
- Nunca criar "documentação ornamental" — toda documentação deve servir à operação do repositório.
- Nunca esconder risco estrutural num PR.
