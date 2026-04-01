# Instruções para Trabalhadores

## Setup Inicial

```bash
# 1. Entrar na worktree
cd /home/ckl3n/dev/wt-matching  # ou wt-upsert

# 2. Ler contexto do projeto
cat QUICKSTART.md
cat docs/STATUS.md
cat docs/WORK_ITEMS.md

# 3. Ler sua tarefa específica
cat TASK.md

# 4. Ativar ambiente
source .venv/bin/activate
```

---

## Workflow de Trabalho

### 1. Implementar em ciclos pequenos
```bash
# Fazer mudança pequena
# ... editar código ...

# Testar
pytest -q

# Commitar
git add .
git commit -m "feat(modulo): descrição clara"

# Repetir
```

### 2. Ao finalizar
```bash
# Validar testes
pytest -q
pytest --cov

# Push
git push -u origin <sua-branch>
```

---

## Template de Report

Quando terminar, reporte ao Gerenciador:

```
TAREFA: WI-XXX
BRANCH: agent/nome-branch
COMMIT: abc1234
STATUS: ✅ Concluído / ⚠️ Bloqueado / 🔄 Em progresso

TESTES: 
- pytest -q: ✅ XX passando
- cobertura: XX%

MUDANÇAS:
- Arquivo X: descrição
- Arquivo Y: descrição

PENDÊNCIAS/RISCOS:
- (se houver)

PRÓXIMO PASSO:
- (se aplicável)
```

---

## Regras Importantes

1. **Commits pequenos** e semânticos
2. **Testar antes de cada commit**
3. **Não fazer merge** em main (só o Gerenciador faz)
4. **Reportar bloqueios** imediatamente
5. **Seguir TASK.md** da sua worktree
