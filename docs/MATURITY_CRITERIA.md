# Critérios de Maturidade — saída do estágio bootstrap

Este documento define as condições verificáveis e binárias para considerar o sistema
operacionalmente confiável. Enquanto qualquer critério estiver "não provado", o projeto
está no estágio bootstrap.

**Última revisão**: 2026-04-01
**Status geral**: 🔴 Bootstrap — nenhum critério provado

---

## Critérios do caminho crítico

| # | Critério | Como verificar | Status |
|---|----------|----------------|--------|
| C1 | Identidade de item preservada sob reimportação com dados reais | Importar a mesma fonte duas vezes com dados reais; confirmar que source_key é estável e não gera duplicatas | ❌ Não provado |
| C2 | Matching funciona sob crescimento de acervo | Importar acervo com N > 1000 itens reais; confirmar que candidatos de matching são gerados sem degradação | ❌ Não provado |
| C3 | Revisão humana fecha o ciclo de reconciliação | Executar fluxo completo: importar → matching → revisar na UI → confirmar merge; confirmar que decisão persiste | ❌ Não provado |
| C4 | Ingestão real não implode premissas do domínio | Usar parser real (não mock) com dados heterogêneos; confirmar que normalização, aliases e upsert se comportam conforme esperado | ❌ Não provado |

---

## Critérios de suporte

| # | Critério | Como verificar | Status |
|---|----------|----------------|--------|
| S1 | Parser real disponível (CSV ou JSON) | MockParser substituído por parser que lê arquivo real | ❌ Não provado |
| S2 | DTOs usados na UI | Streamlit usa mappers em vez de acessar domínio diretamente | ❌ Não provado |
| S3 | mypy enforçado em hooks | pre-push bloqueia erros de tipo | ❌ Não provado |
| S4 | Trilha de auditoria de reconciliação | Decisões de merge registradas e consultáveis | ❌ Não provado |

---

## Como atualizar este documento

Quando um critério for satisfeito:
1. Alterar o campo Status de `❌ Não provado` para `✅ Provado`.
2. Adicionar data e referência ao commit ou evidência.
3. Atualizar o "Status geral" no cabeçalho.

Critérios não são marcados como provados por testes unitários isolados —
exigem execução com dados reais ou integração end-to-end.
