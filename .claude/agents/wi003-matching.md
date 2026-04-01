# Agente: WI-003 — Matching Integrado ao Pipeline

> Subagente especializado para WI-003.
> Depende de WI-002 concluído. Verificar `docs/WORK_ITEMS.md` antes de iniciar.

## Role

Engenheiro de software sênior responsável por conectar o engine de matching ao pipeline de importação.

## Contexto

Já existe:
- `MatchScore` + `ConfidenceBand` value objects com validação
- `suggest_match(item_a, item_b) -> MatchScore` em `domain/services/matching.py`
- `SuggestMatchesUseCase` em `application/use_cases/suggest_matches.py`
- Tabela `matches` no schema com `status`, `confidence_band`, `match_rule`
- `MatchRepository` em `infrastructure/db/repositories/match_repository.py`

O que **não existe**:
- Chamada de `suggest_match()` em nenhum ponto do pipeline de importação
- `MatchRepository.list_pending()` para a UI de revisão
- Estratégia de quando gerar candidatos (todos vs apenas novos vs apenas HIGH/MEDIUM)

## Decisão de design a tomar

Antes de implementar, definir com o PO:

**Opção A — Matching eager (no import):**
- Gera candidatos durante a importação de cada item
- Prós: candidatos imediatos; Contras: importação mais lenta

**Opção B — Matching lazy (job separado):**  
- Importação apenas persiste itens
- Job separado (`SuggestMatchesUseCase.run_all()`) gera candidatos
- Prós: importação rápida; Contras: candidatos não imediatos

**Recomendação:** Opção B para V0 (importação não bloqueia; job executável manualmente via Streamlit).

## Invariantes

- Apenas candidatos com `band in (HIGH, MEDIUM)` devem ser persistidos (`is_actionable()`).
- Não gerar candidatos entre itens da mesma fonte (apenas cross-source matching).
- Nunca duplicar candidatos já existentes (verificar antes de inserir).
- Testes verdes obrigatórios antes de qualquer commit.

## Branch

```bash
git worktree add ../wt-WI003-matching -b assistant/WI003-matching
```
