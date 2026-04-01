# Início Rápido

## Setup (5 minutos)

```bash
# 1. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -e .[dev]

# 3. Instalar hooks de qualidade
make install-hooks

# 4. Rodar testes
pytest -q
```

## Desenvolvimento

### Antes de começar qualquer tarefa
Ler nesta ordem:
1. `INSTRUCTIONS.md` — regras obrigatórias
2. `docs/STATUS.md` — estado atual e prioridades
3. `docs/WORK_ITEMS.md` — tarefas ativas

### Criar nova tarefa

```bash
# 1. Criar worktree isolada
git worktree add ../wt-minha-tarefa -b agent/minha-tarefa

# 2. Trabalhar na worktree
cd ../wt-minha-tarefa

# 3. Fazer mudanças pequenas
# ... editar código ...

# 4. Testar antes de commit
pytest -q

# 5. Commit semântico
git add .
git commit -m "feat(modulo): descrição clara"

# 6. Repetir 3-5 até concluir
```

### Rodar aplicação

```bash
streamlit run app/streamlit_app.py
```

## Estrutura do Código

```
src/catalogo_acervo/
├── application/        # Casos de uso
├── domain/            # Entidades e serviços
├── infrastructure/    # DB, repositórios, parsers
└── interfaces/        # DTOs e mappers (UI ↔ domínio)
```

## Comandos Úteis

```bash
# Testes
pytest -q                    # rodar todos
pytest tests/unit -v         # só unitários
pytest --cov                 # com cobertura

# Qualidade
ruff check .                 # lint
ruff format .                # format
mypy src                     # type check

# Git
git worktree list            # listar worktrees
git worktree remove ../wt-x  # remover worktree
```

## Prioridades Atuais

1. **DTOs e mappers** ✅ (concluído)
2. **Matching operacional** — integrar ao pipeline
3. **Atualização seletiva** — merge por campo
4. **Revisão manual** — UI de reconciliação

**Não fazer agora**: IA, MCP, deploy, UI sofisticada
