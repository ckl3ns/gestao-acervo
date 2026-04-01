# Próximo passo após este PR

## O que este PR entrega
- registro explícito de parsers;
- pipeline de importação que resolve o parser a partir da fonte cadastrada;
- aliases aplicados na normalização durante a importação;
- testes cobrindo registry, aliases e integração do novo pipeline.

## O que ainda não entrega
- a interface Streamlit ainda usa o caso de uso antigo;
- o app ainda não tem CRUD de aliases;
- a importação padrão ainda não troca automaticamente para o pipeline novo.

## Próxima evolução recomendada
1. trocar o `app/streamlit_app.py` para usar `ImportSourceItemsFromSourceUseCase`;
2. adicionar tela simples de aliases no Streamlit;
3. remover a instanciação fixa de `MockParser()` do app;
4. consolidar o caso de uso antigo e o novo em uma única trilha;
5. depois disso, atacar matching + revisão manual.

## Justificativa
Sem isso, o repositório continua com a arquitetura certa e o comportamento errado: a fonte armazena `parser_name`, mas o app ignora essa informação na hora de importar.
