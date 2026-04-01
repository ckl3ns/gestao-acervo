# Workflow do seu lado (PO) — do ZIP até os arquivos na branch principal

Este guia parte destas premissas:

- você **já baixou o ZIP** que eu te entreguei;
- você **já extraiu** o conteúdo em uma pasta com o mesmo nome do ZIP;
- você está **dentro da pasta do repositório** no terminal;
- as **dependências já estão instaladas**;
- o `.git` veio junto no snapshot extraído;
- a branch principal do projeto é **`main`**. Se no seu clone local ela for `master`, troque `main` por `master` nos comandos.

---

## 1. Confirmar que você está no repositório certo

Verifique o caminho atual:

```bash
pwd
```

Verifique se o diretório tem Git:

```bash
git status
```

Se aparecer algo como `fatal: not a git repository`, então o ZIP foi extraído sem o diretório `.git`.
Nesse caso, **pare aqui** e use um clone real do repositório para aplicar manualmente as mudanças.

---

## 2. Ver quais branches existem no snapshot

Liste as branches locais:

```bash
git branch
```

Você deve ver algo como:

```bash
* assistant/governance-agent-operating-model
  main
```

A branch com prefixo `assistant/` é a branch de trabalho que eu preparei.

---

## 3. Confirmar o histórico recente

Veja os commits mais recentes:

```bash
git log --oneline --decorate --graph -n 15
```

Você deve encontrar commits parecidos com estes:

```text
f038f96 docs(progress): record governance task completion
a24cde5 docs(workflow): align process with multi-agent worktree model
752e2fc docs(status): add project status and work item registry
5f2a96e docs(governance): define agent operating rules
e4bf033 chore(repo): enforce tests before commit with git hooks
```

Se isso não aparecer, você não está olhando para a versão certa.

---

## 4. Conferir em qual branch você está

```bash
git branch --show-current
```

Se não estiver na branch de trabalho, troque:

```bash
git checkout assistant/governance-agent-operating-model
```

---

## 5. Rodar os testes antes de qualquer coisa

Mesmo que eu já tenha rodado, **rode de novo**. Confiança cega em snapshot é coisa de amador.

```bash
pytest -q
```

O esperado é algo como:

```text
8 passed
```

Se falhar, você **não** leva isso para a branch principal.

---

## 6. Instalar os hooks locais

Esse passo garante que, no seu clone, novos commits só aconteçam se os testes passarem.

```bash
make install-hooks
```

Se quiser confirmar a configuração:

```bash
git config --get core.hooksPath
```

O esperado é:

```text
.githooks
```

---

## 7. Revisar os arquivos criados/alterados

Veja o diff da branch de trabalho em relação à principal:

```bash
git diff --stat main..assistant/governance-agent-operating-model
```

Para ver o diff completo:

```bash
git diff main..assistant/governance-agent-operating-model
```

Arquivos importantes para revisar primeiro:

```text
INSTRUCTIONS.md
AGENTS.md
README.md
docs/workflow.md
docs/STATUS.md
docs/WORK_ITEMS.md
.githooks/pre-commit
scripts/install-hooks.sh
Makefile
```

---

## 8. Ler a documentação mínima obrigatória

Leia, nesta ordem:

```bash
cat INSTRUCTIONS.md
```

```bash
cat AGENTS.md
```

```bash
cat docs/workflow.md
```

```bash
cat docs/STATUS.md
```

```bash
cat docs/WORK_ITEMS.md
```

Se preferir abrir no editor:

```bash
code .
```

ou qualquer editor que você use.

---

## 9. Validar que a branch principal local está limpa

Troque para a principal:

```bash
git checkout main
```

Confirme que não há lixo local:

```bash
git status
```

O esperado é algo como:

```text
nothing to commit, working tree clean
```

Se houver mudanças soltas, resolva isso antes de seguir.

---

## 10. Atualizar a branch principal local

Se esse diretório tem `origin` configurado, atualize a referência remota:

```bash
git fetch origin
```

Depois alinhe sua branch principal local:

```bash
git pull origin main
```

Se você estiver usando `master`, então:

```bash
git pull origin master
```

---

## 11. Conferir novamente a diferença entre principal e branch de trabalho

```bash
git log --oneline main..assistant/governance-agent-operating-model
```

Esse comando mostra os commits que entrarão no merge.

---

## 12. Fazer merge local da branch de trabalho na principal

Estando em `main`:

```bash
git merge --no-ff assistant/governance-agent-operating-model
```

Use `--no-ff` para preservar o bloco de trabalho como unidade histórica visível.

Se houver conflito, resolva no editor, depois:

```bash
git add .
```

```bash
git commit
```

Se não houver conflito, o merge será concluído automaticamente.

---

## 13. Rodar os testes de novo após o merge

Esse passo é obrigatório.

```bash
pytest -q
```

Se falhar agora, reverta o merge antes de empurrar para o remoto.

Para abortar um merge ainda em andamento:

```bash
git merge --abort
```

Para reverter um merge já concluído localmente, antes do push:

```bash
git reset --hard HEAD~1
```

Cuidado: `reset --hard` destrói mudanças locais não commitadas.

---

## 14. Inspecionar o resultado final na principal

Veja os commits recentes:

```bash
git log --oneline --decorate --graph -n 20
```

Veja o estado:

```bash
git status
```

Veja os arquivos relevantes:

```bash
ls -la
ls -la docs
ls -la .githooks
ls -la scripts
```

---

## 15. Enviar a principal para o remoto

Agora sim, empurre para o GitHub:

```bash
git push origin main
```

Se sua principal for `master`:

```bash
git push origin master
```

---

## 16. Opcional: apagar a branch local de trabalho depois do merge

Só faça isso **depois** de confirmar que o push foi bem-sucedido.

```bash
git branch -d assistant/governance-agent-operating-model
```

Se quiser apagar também no remoto, e ela existir lá:

```bash
git push origin --delete assistant/governance-agent-operating-model
```

---

## 17. Como começar a próxima grande tarefa no modelo novo

Com a principal atualizada, crie uma nova branch de trabalho para a próxima entrega.

Exemplo:

```bash
git checkout main
```

```bash
git pull origin main
```

```bash
git checkout -b assistant/update-selective-sync
```

Se você quiser usar worktree, que é o recomendado para múltiplos agentes:

```bash
git worktree add ../wt-update-selective-sync -b assistant/update-selective-sync main
```

Isso cria um diretório isolado para essa grande tarefa.

---

## 18. Regra operacional para qualquer trabalho futuro

Antes de delegar uma nova tarefa para um agente, faça esta checagem:

1. branch principal limpa;
2. hooks instalados;
3. `INSTRUCTIONS.md` e `AGENTS.md` revisados;
4. nova tarefa registrada em `docs/WORK_ITEMS.md`;
5. trabalho em branch própria;
6. se for tarefa grande, use worktree própria;
7. commits pequenos, semânticos e com testes passando.

---

## 19. Checklist final curto

Quando você quiser só validar rápido, use esta sequência:

```bash
git branch
pytest -q
make install-hooks
git checkout main
git fetch origin
git pull origin main
git log --oneline main..assistant/governance-agent-operating-model
git merge --no-ff assistant/governance-agent-operating-model
pytest -q
git push origin main
```

---

## 20. Sinal de que você está fazendo errado

Pare imediatamente se acontecer qualquer uma destas coisas:

- você não sabe em qual branch está;
- `pytest -q` falha e você pensa em seguir mesmo assim;
- o merge entra na principal sem você ter lido o diff;
- a tarefa não está registrada em `docs/WORK_ITEMS.md`;
- mais de um agente mexe no mesmo diretório sem worktree isolada;
- alguém faz commit grande e misturado “para ganhar tempo”.

Isso não ganha tempo. Isso compra dívida.

---

## 21. O que fazer se quiser abrir PR em vez de merge local direto

Se preferir usar PR no GitHub:

1. faça checkout da branch de trabalho:

```bash
git checkout assistant/governance-agent-operating-model
```

2. publique a branch, se ainda não existir no remoto:

```bash
git push -u origin assistant/governance-agent-operating-model
```

3. abra o PR no GitHub com base em `main`;
4. revise o diff;
5. confirme os testes;
6. faça o merge no GitHub;
7. atualize localmente:

```bash
git checkout main
git pull origin main
```

Esse fluxo é mais auditável quando houver vários agentes trabalhando em paralelo.

---

## 22. Resumo brutalmente honesto

Seu trabalho como PO não é “só aprovar”.
Seu trabalho é impedir que o repositório vire um lixão coordenado por agentes que escrevem código sem memória operacional.

Se você não controlar:
- branch,
- worktree,
- status,
- testes,
- e merge,

então você não está conduzindo um time. Está só terceirizando caos.
