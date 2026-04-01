# Implementation Plan: bootstrap-narrative-alignment

## Overview

Calibrar a linguagem de todos os documentos do repositório para refletir o estágio real do projeto: bootstrap funcional, não maturidade operacional. Nenhum código é alterado — apenas documentos.

A ordem de execução respeita a dependência de referências: `docs/MATURITY_CRITERIA.md` é criado primeiro para que os demais documentos possam referenciá-lo sem links quebrados.

## Tasks

- [x] 1. Criar docs/MATURITY_CRITERIA.md
  - Criar o arquivo novo com a estrutura completa definida no design
  - Incluir tabela de critérios do caminho crítico (C1–C4) com status `❌ Não provado`
  - Incluir tabela de critérios de suporte (S1–S4) com status `❌ Não provado`
  - Incluir instrução de atualização ao final do documento
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 2. Modificar ANALISE_CONFORMIDADE.md
  - [x] 2.1 Corrigir linguagem de produção no cabeçalho e na conclusão
    - Substituir `✅ APROVADO PARA PRODUÇÃO` por `✅ CONFORME — padrões de processo do estágio bootstrap` no campo Status do cabeçalho
    - Substituir título da conclusão `✅ REPOSITÓRIO APROVADO PARA PRODUÇÃO` por `✅ REPOSITÓRIO CONFORME COM PADRÕES DE PROCESSO (estágio bootstrap)`
    - Substituir corpo da conclusão pela versão calibrada com link para `docs/MATURITY_CRITERIA.md`
    - _Requirements: 1.1, 1.2, 1.4_
  - [x] 2.2 Adicionar seção "O que o bootstrap ainda não provou"
    - Inserir a seção antes da "Conclusão" com a tabela dos 4 eixos (identidade, matching, revisão humana, ingestão real)
    - Incluir link para `docs/MATURITY_CRITERIA.md` na seção
    - _Requirements: 1.3, 4.5_

- [x] 3. Modificar docs/STATUS.md
  - [x] 3.1 Anotar seção "Concluído e funcional" com contexto de bootstrap
    - Renomear cabeçalho de `### ✅ Concluído e funcional` para `### ✅ Concluído e funcional no bootstrap`
    - Inserir nota de contexto logo abaixo do cabeçalho com link para `docs/MATURITY_CRITERIA.md`
    - _Requirements: 2.1, 2.3_
  - [x] 3.2 Expandir seção de riscos
    - Adicionar dois itens sobre caminho crítico não provado
    - Adicionar link para `docs/MATURITY_CRITERIA.md` nos novos itens
    - _Requirements: 2.2, 4.5_

- [x] 4. Modificar README.md
  - Adicionar seção "O que este bootstrap entrega — e o que ele não prova" logo após a seção "Fluxo mínimo disponível"
  - Incluir lista do que está entregue e do que ainda não foi provado
  - Incluir link para `docs/MATURITY_CRITERIA.md` ao final da seção
  - _Requirements: 3.1, 3.2, 3.3, 4.5_

- [x] 5. Modificar AGENTS.md
  - [x] 5.1 Adicionar referência a MATURITY_CRITERIA.md em "Fonte de verdade para contexto operacional"
    - Inserir `- \`docs/MATURITY_CRITERIA.md\`` na lista de fontes de verdade
    - _Requirements: 5.3_
  - [x] 5.2 Adicionar referência a MATURITY_CRITERIA.md em "Estado atual"
    - Inserir linha apontando para `docs/MATURITY_CRITERIA.md` como fonte dos critérios verificáveis de saída do bootstrap
    - _Requirements: 5.3_

- [x] 6. Verificar consistência — checar as 4 propriedades de corretude
  - Executar as verificações textuais definidas no design para confirmar que todas as propriedades são satisfeitas
  - **Property 1 — Ausência de linguagem de produção**: `grep -ri "aprovado para produção\|pronto para produção" ANALISE_CONFORMIDADE.md docs/STATUS.md README.md AGENTS.md` deve retornar vazio
  - **Property 2 — Presença de linguagem de bootstrap calibrada**: `grep -li "bootstrap funcional\|estágio bootstrap\|bootstrap local-first" ANALISE_CONFORMIDADE.md docs/STATUS.md README.md` deve retornar os 3 arquivos
  - **Property 3 — Critérios binários e completos**: `grep -c "Não provado\|✅ Provado" docs/MATURITY_CRITERIA.md` deve retornar ≥ 4
  - **Property 4 — Referência cruzada para MATURITY_CRITERIA.md**: `grep -l "MATURITY_CRITERIA" ANALISE_CONFORMIDADE.md docs/STATUS.md README.md AGENTS.md` deve retornar os 4 arquivos
  - _Requirements: 1.1, 1.2, 4.1, 4.3, 4.5, 5.1, 5.2_
