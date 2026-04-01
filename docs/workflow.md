# Workflow de colaboração

## Modelo operacional adotado
Este repositório deve funcionar como um time adaptado para agentes de IA:
- **PO / cliente**: o mantenedor humano define prioridades e valida entregas.
- **Scrum Master + Tech Lead**: um agente com responsabilidade de coordenação técnica quebra trabalho, protege escopo, impõe disciplina e garante qualidade.
- **Agentes executores**: atuam como equipe de desenvolvimento e implementam tarefas delimitadas em worktrees isoladas.

O princípio central é simples: **uma grande tarefa por worktree/branch, uma mudança por commit, testes antes de commit, status sempre documentado**.

## Fonte de verdade operacional
Antes de iniciar qualquer tarefa, ler nesta ordem:
1. `INSTRUCTIONS.md`
2. `AGENTS.md`
3. `docs/STATUS.md`
4. `docs/WORK_ITEMS.md`
5. `docs/workflow.md`
6. `README.md`
7. documentação técnica relevante

## Regra de ouro
Pergunta obrigatória antes de agir:

1. Isso aproxima o núcleo do objetivo real?
2. Ou isso só produz sensação de progresso?

Se for a segunda opção, a tarefa deve ser adiada.

## Estratégia de branches e worktrees

### Branch principal
- `main`: sempre estável, testada e pronta para merge.

### Branch por grande tarefa
Padrões recomendados:
- `assistant/<tema-curto>`
- `codex/<tema-curto>`
- `agent/<tema-curto>`
- `user/<tema-curto>`

Exemplos:
- `assistant/update-selective-sync`
- `codex/matching-candidate-persistence`
- `agent/manual-review-ui`

### Worktree por grande tarefa
Cada grande tarefa deve ter worktree própria.

Exemplo:
```bash
git worktree add ../wt-update-selective-sync -b assistant/update-selective-sync
```

Regras:
- não reutilizar a mesma worktree para tarefa diferente;
- registrar worktree e branch em `docs/WORK_ITEMS.md`;
- remover a worktree ao encerrar a tarefa.

## Convenção de commits
Commits devem ser pequenos, reversíveis e semanticamente claros.

Padrões aceitos:
- `feat(...)`
- `fix(...)`
- `refactor(...)`
- `test(...)`
- `docs(...)`
- `chore(...)`

Exemplos bons:
- `fix(normalization): fold diacritics in canonical text`
- `feat(app): wire source-driven imports`
- `docs(governance): define agent operating rules`

Exemplos ruins:
- `update`
- `misc`
- `fix stuff`

## Regra obrigatória de commit
**Nenhum commit deve ser feito com testes falhando.**

Fluxo obrigatório:
1. implementar mudança pequena;
2. rodar `pytest -q`;
3. atualizar `docs/STATUS.md` e/ou `docs/WORK_ITEMS.md` quando aplicável;
4. commitar.

O repositório inclui hook de pre-commit para reforçar essa regra.
Instalação:
```bash
make install-hooks
```

## Fluxo por tarefa

### 1. Preparação
- confirmar prioridade com base em `docs/STATUS.md`;
- abrir ou receber um item em `docs/WORK_ITEMS.md`;
- criar branch e worktree.

### 2. Execução
- fazer uma mudança pequena;
- testar;
- documentar progresso;
- commitar;
- repetir.

### 3. Handoff ou conclusão
- registrar últimos commits;
- registrar testes executados;
- registrar pendências e riscos;
- registrar próximo passo lógico.

## Documentação obrigatória durante a execução

### `docs/STATUS.md`
Usado para:
- visão executiva do estado atual;
- prioridades do backlog;
- riscos ativos;
- últimas entregas relevantes.

### `docs/WORK_ITEMS.md`
Usado para:
- controle de tarefas ativas;
- vínculo entre tarefa, branch, worktree e responsável;
- handoff entre agentes;
- rastreio de testes e próximos passos.

## Checklist de PR
Antes de abrir ou aprovar PR:
- [ ] testes verdes
- [ ] commits pequenos e semânticos
- [ ] escopo coerente com a branch
- [ ] `docs/STATUS.md` e `docs/WORK_ITEMS.md` atualizados, se aplicável
- [ ] documentação técnica atualizada, se a arquitetura ou o processo mudaram
- [ ] nenhuma deriva para IA/MCP/deploy antes do núcleo

## Ordem recomendada do backlog

### Fase 1 — Integridade do núcleo
1. atualização seletiva real por fonte
2. testes mais fortes de importação/sincronização
3. endurecimento da rastreabilidade operacional

### Fase 2 — Reconciliação
4. matching operacional
5. deduplicação/persistência de candidatos
6. revisão manual
7. trilha de auditoria

### Fase 3 — Operação mínima útil
8. filtros e busca melhores
9. telas de revisão
10. relatórios simples

### Fase 4 — Só depois
11. IA
12. MCP
13. deploy
14. integrações externas mais amplas

## Política contra dispersão
Interromper imediatamente qualquer tarefa que comece a puxar para:
- chatbot;
- embeddings;
- MCP operacional;
- deploy;
- UI sofisticada;
- autenticação complexa.

## Fluxo alternativo quando integração GitHub falhar
Se o conector não permitir ciclo completo de edição:
1. exportar `.zip` do branch atual;
2. trabalhar localmente mantendo histórico Git;
3. devolver `.zip` com branch pronta e commits preservados;
4. abrir PR manualmente.

## Interruptor de emergência
Se uma branch começar a misturar escopos ou crescer sem nitidez:
- congelar a branch;
- registrar o estado em `docs/WORK_ITEMS.md`;
- abrir nova branch menor para o próximo bloco.

---

## Ciclo de Vida de uma Branch

```
1. CRIAR
   git pull origin main
   git checkout -b agent/minha-tarefa
   git push -u origin agent/minha-tarefa

2. TRABALHAR (em ciclos pequenos)
   ... implementar ...
   pytest -q
   git add . && git commit -m "feat(...): descrição"
   git push

3. VALIDAR
   - testes passando
   - cobertura >= 70%
   - documentação atualizada
   - git status limpo

4. MERGE (Scrum Master faz)
   git checkout main
   git pull origin main
   git merge agent/minha-tarefa --no-edit
   pytest -q
   git push origin main

5. LIMPEZA
   git branch -d agent/minha-tarefa
   git push origin --delete agent/minha-tarefa
   git worktree remove ../wt-minha-tarefa (se aplicável)
```

---

## Checklist: Antes de Reportar Conclusão

- [ ] `pytest -q` passando
- [ ] `git status` limpo (nada pendente)
- [ ] Documentação atualizada (STATUS.md, WORK_ITEMS.md)
- [ ] Branch no remote
- [ ] README ou TASK.md reflete último estado

---

## Regras de Ouro (Lições Aprendidas)

1. **Documentação é código** — atualize junto ou não commite
2. **Worktree limpa** — só abandone quando `git status` estiver limpo
3. **Branch é temporária** — delete após merge
4. **Pull antes de trabalhar** — sempre sincronizar antes de criar branch
5. **Force push = emergência** — comunicar se precisar
6. **Menos markdown** — cada documento deve ter propósito claro

Ver também: `docs/LESSONS_LEARNED.md`
