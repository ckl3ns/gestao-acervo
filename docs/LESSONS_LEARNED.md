# Lições Aprendidas

**Última atualização**: 2026-04-02

---

## Problemas Encontrados e Como Evitá-los

### 1. 📋 Documentação Desatualizada

**Problema**: STATUS.md e WORK_ITEMS.md não refletiam a realidade do código. Commits mencionados não existiam no repositório. Número de testes estava errado (42 vs 52 real).

**Impacto**: Perda de credibilidade na documentação, dificuldade de rastrear progresso real.

**Como evitar**:
- ✅ **Regra**: Antes de qualquer trabalho, reconciliar documentação com `git log`
- ✅ **Regra**: Atualizar STATUS.md e WORK_ITEMS.md IMEDIATAMENTE após cada commit
- ✅ **Regra**: Nunca commitar código sem atualizar documentação correspondente

---

### 2. 🔀 Divergência de Histórico Git

**Problema**: Remote tinha commits que não existiam localmente, causando necessidade de force push.

**Causa**: Worktrees de sessões anteriores ou pushes diretos ao remote sem sincronização.

**Como evitar**:
- ✅ **Regra**: Sempre fazer `git pull --rebase` antes de iniciar trabalho em worktree
- ✅ **Regra**: Nunca fazer push direto sem verificar se main está atualizada
- ✅ **Regra**: Worktrees devem começar com `git pull origin main` dentro da worktree

---

### 3. 🗑️ Limpeza de Branches Obsoletas

**Problema**: 3 branches remotas obsoletas (`assistant/infra-maturidade-dev`, `assistant/test-tree-sha`, `codex/execute-initial-bootstrap-based-on-documentation`) poluíam o repositório.

**Causa**: Falta de policy para limpar branches após merge ou cancelamento.

**Como evitar**:
- ✅ **Regra**: Branch de tarefa = branch temporária. Após merge, DELETE a branch.
- ✅ **Regra**: Após worktree concluída, remover imediatamente após merge
- ✅ **Regra**: `git push --delete origin <branch>` faz parte do fluxo de conclusão

---

### 4. 📚 Excesso de Documentação Ornamental

**Problema**: 41 arquivos markdown, muitos redundantes ou de bootstrap (CLAUDE.md, instrucoes-agente-codex-bootstrap-v2.md, etc).

**Impacto**: Dificulta encontrar informação relevante, confunde novos participantes.

**Como evitar**:
- ✅ **Regra**: Documentação deve servir operação, não impressionar
- ✅ **Regra**: Cada documento deve responder "para que serve?" claramente
- ✅ **Regra**: Arquivar (não deletar) documentação de bootstrap em `.archive/`

---

### 5. 🌳 Worktree com Arquivos Modificados

**Problema**: Ao tentar remover wt-matching, git reclamou de arquivos modificados/untracked.

**Causa**: Agente deixou mudanças não commitadas na worktree antes de finalizar.

**Como evitar**:
- ✅ **Regra**: Worktree só é concluída quando ESTÁ LIMPA (working tree clean)
- ✅ **Regra**: Verificar `git status` antes de abandonar worktree
- ✅ **Regra**: Se worktree tem trabalho incompleto, commitar ou fazer stash antes de reportar

---

### 6. 🔒 Force Push Necessário

**Problema**: Precisei usar `--force` para sobrescrever histórico divergido.

**Causa**: Falta de comunicação entre sessões de trabalho.

**Como evitar**:
- ✅ **Regra**: NUNCA fazer force push em main ou branches ativas
- ✅ **Regra**: Se force push necessário, comunicar imediatamente ao time
- ✅ **Regra**: Worktrees devem sincronizar com main ANTES de criar novas branches

---

## Lições Positivas (Manter)

### ✅ Governança Funcionou
- hooks de pre-commit/pre-push impediram código quebrado
- workflow de worktrees permitiu execução paralela
- testes obrigatórios antes de commit funcionaram

### ✅ DTOs e Mappers Resolveram Dívito Técnico
- interfaces/dto e interfaces/mappers estavam vazios (débito)
- Implementação foi rápida (~1 commit)
- Resultado: 52→53 testes, cobertura 72%→75%

### ✅ Documentação Consolidada Ajuda
- Reduzir de 41 para ~10 markdown arquivos foi bom
- QUICKSTART.md para onboarding rápido funcionou
- STATUS.md e WORK_ITEMS.md limpos são mais úteis

---

## Regras de Ouro (Atualizar workflow.md)

1. **Documentação é código** — atualize junto ou não commite
2. **Worktree limpa** — só abandone quando `git status` estiver limpo
3. **Branch é temporária** — delete após merge
4. **Pull antes de trabalhar** — sempre sincronizar antes de criar branch
5. **Force push = emergência** — comunicar se precisar
6. **Menos markdown** — cada documento deve ter propósito claro

---

## Revisões Necessárias no Processo

- [x] workflow.md: adicionar seção de "Branch lifecycle" (criar → trabalho → merge → delete)
- [x] workflow.md: adicionar checklist de "antes de abandonar worktree"
- [ ] STATUS.md: regra de atualização deve mencionar reconciliação com git log
