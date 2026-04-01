# /prime-context — Injetar contexto completo do projeto

Execute estes comandos sequencialmente para ter o estado completo antes de iniciar trabalho:

```bash
echo "=== QUALIDADE ATUAL ===" && make quality 2>&1 | tail -5
echo ""
echo "=== COBERTURA ===" && python -m pytest --cov --cov-report=term-missing -q 2>&1 | tail -10
echo ""
echo "=== STATUS DO PRODUTO ===" && cat docs/STATUS.md
echo ""
echo "=== BACKLOG ATIVO ===" && cat docs/WORK_ITEMS.md
echo ""
echo "=== ÚLTIMOS COMMITS ===" && git log --oneline -10
echo ""
echo "=== BRANCHES ATIVAS ===" && git branch -a
```

Após executar, forneça um resumo de:
1. Estado dos testes (N passando, cobertura X%)
2. WI em andamento (se houver)
3. Próximo WI a atacar
4. Qualquer blocker ou risco identificado
