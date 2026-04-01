# Regras: Estilo Python

> Estas regras são carregadas pelo Claude Code a cada turno junto com CLAUDE.md.
> Aplicam-se a todo código Python do projeto.

## Formatação e lint

- **Ruff** é o único linter/formatter. Nunca usar black, isort separado, flake8.
- Linha máxima: 100 caracteres (`line-length = 100` no pyproject.toml).
- Imports: sempre ordenados pelo ruff (isort integrado). Rodar `python -m ruff check --fix` antes de commitar.
- `from __future__ import annotations` obrigatório em todos os módulos de domínio e application.

## Tipagem

- Type hints completos em toda função e método público.
- Retornos explícitos: nunca omitir `-> None` mesmo em funções que não retornam.
- Usar `X | None` (union moderna, Python 3.10+) em vez de `Optional[X]`.
- Usar `X | Y` em vez de `Union[X, Y]`.
- `Protocol` para contracts e interfaces — nunca ABC para esse fim.
- `model_config = {"frozen": True}` em todos os value objects Pydantic.

## Estrutura de módulos

- Arquivo ideal: 200–400 linhas. Máximo: 600 linhas.
- Se passar de 600 linhas: dividir em sub-módulos por responsabilidade.
- Organizar por domínio/responsabilidade, nunca por tipo (ex: não criar `utils.py` genérico).
- Cada módulo público deve ter `__all__` se expõe mais de 3 símbolos.

## Nomenclatura

- Funções e variáveis: `snake_case`.
- Classes: `PascalCase`.
- Constantes de módulo: `UPPER_SNAKE_CASE`.
- Parâmetros de função privada (só lidos, nunca mutados): prefixo `_` explícito quando necessário.
- Nunca usar nomes genéricos como `data`, `info`, `item` — ser específico.

## Docstrings

- Escrever APENAS quando o nome e tipo não explicam o "por quê".
- Explicar decisões de design, não reimplementar em prosa o que o código já diz.
- Formato: uma linha para módulos simples, Google-style para funções complexas.
- Documentar anti-padrões: `# ERRADO: ...` / `# CERTO: ...` nos locais críticos.

## Proibições

- Nunca `import *`.
- Nunca importar `sqlite3` no domínio ou aplicação — apenas na infraestrutura.
- Nunca importar `streamlit` fora de `app/`.
- Nunca usar `Any` sem justificativa explícita em comentário.
- Nunca usar `print()` em código de produção (usar `ProcessingLogger`).
- Nunca usar `time.sleep()` em testes.
