# Requirements Document

## Introduction

O repositório é um bootstrap técnico bem estruturado (nota 7.5–8/10): entrega espinha dorsal arquitetural coerente e loop de desenvolvimento funcionando. O problema central é que a documentação atual usa linguagem de "APROVADO PARA PRODUÇÃO" para um projeto que ainda não provou o caminho crítico com dados reais.

Esta feature corrige a narrativa e a documentação para refletir o estágio real: bootstrap funcional, não robustez operacional. O objetivo não é rebaixar o trabalho feito — é calibrar a linguagem para que ela seja honesta sobre o que foi provado e o que ainda não foi.

## Glossary

- **Bootstrap**: estágio inicial do projeto onde a espinha dorsal arquitetural está implementada e o loop de desenvolvimento funciona, mas o caminho crítico com dados reais ainda não foi provado.
- **Caminho crítico**: conjunto de fluxos que precisam funcionar com dados reais para o sistema ser considerado operacionalmente confiável — identidade de item sob reimportações reais, matching sob crescimento de acervo, revisão humana fechando o ciclo, ingestão real sem implodir premissas do domínio.
- **Narrativa**: linguagem usada nos documentos do repositório para descrever o estado e a maturidade do projeto.
- **Critério de maturidade**: condição verificável que, quando satisfeita, indica que o projeto avançou do estágio bootstrap para o estágio operacional.
- **ANALISE_CONFORMIDADE.md**: documento que avalia conformidade do repositório com padrões de processo — atualmente usa linguagem de produção incorreta para o estágio atual.
- **docs/STATUS.md**: documento de estado atual do produto — usa "Concluído e funcional" para itens que são funcionais no bootstrap mas não provados com dados reais.
- **README.md**: documento de entrada do repositório — menciona "Bootstrap" no título mas não deixa explícitas as limitações do estágio atual.

---

## Requirements

### Requirement 1: Corrigir ANALISE_CONFORMIDADE.md

**User Story:** Como mantenedor do projeto, quero que o ANALISE_CONFORMIDADE.md reflita o estágio real de bootstrap, para que nenhum leitor interprete o repositório como pronto para produção.

#### Acceptance Criteria

1. THE ANALISE_CONFORMIDADE.md SHALL substituir o status "✅ APROVADO PARA PRODUÇÃO" por um status que reflita conformidade com padrões de processo de bootstrap.
2. THE ANALISE_CONFORMIDADE.md SHALL substituir a conclusão "REPOSITÓRIO APROVADO PARA PRODUÇÃO" por uma conclusão que afirme que o repositório está em conformidade com os padrões de processo do estágio bootstrap.
3. THE ANALISE_CONFORMIDADE.md SHALL incluir uma seção explícita listando o que o bootstrap ainda não provou: identidade de item sob reimportações reais, matching sob crescimento de acervo, revisão humana fechando o ciclo, ingestão real sem implodir premissas do domínio.
4. WHEN um leitor lê o ANALISE_CONFORMIDADE.md, THE documento SHALL deixar claro que "conformidade com padrões de processo" é diferente de "pronto para uso operacional com dados reais".

### Requirement 2: Calibrar docs/STATUS.md

**User Story:** Como mantenedor do projeto, quero que o STATUS.md use linguagem calibrada para o estágio bootstrap, para que a seção "Concluído e funcional" não seja confundida com maturidade operacional.

#### Acceptance Criteria

1. THE docs/STATUS.md SHALL renomear ou anotar a seção "✅ Concluído e funcional" para deixar claro que os itens listados são funcionais no contexto do bootstrap, não em produção com dados reais.
2. THE docs/STATUS.md SHALL manter os itens da seção de riscos conhecidos e, se necessário, expandir com riscos relacionados ao caminho crítico ainda não provado.
3. WHEN um agente lê docs/STATUS.md, THE documento SHALL comunicar claramente qual é o estágio atual do projeto sem ambiguidade sobre maturidade operacional.

### Requirement 3: Revisar README.md

**User Story:** Como desenvolvedor que acessa o repositório pela primeira vez, quero que o README.md deixe explícito que o projeto é um bootstrap com limitações conhecidas, para que eu não superestime a maturidade do sistema.

#### Acceptance Criteria

1. THE README.md SHALL incluir uma seção ou nota explícita que descreva o que o bootstrap entrega e o que ele ainda não prova.
2. THE README.md SHALL manter o título "Bootstrap" e reforçar esse posicionamento no corpo do documento.
3. IF um leitor lê apenas o README.md, THEN THE documento SHALL ser suficiente para comunicar que o projeto não está em estágio operacional com dados reais.

### Requirement 4: Criar documento de critérios de maturidade

**User Story:** Como mantenedor do projeto, quero um documento que defina os critérios verificáveis para sair do estágio bootstrap, para que o time saiba exatamente o que precisa ser provado antes de considerar o sistema operacionalmente confiável.

#### Acceptance Criteria

1. THE docs/MATURITY_CRITERIA.md SHALL listar cada critério de maturidade como uma condição verificável e binária (provado / não provado).
2. THE docs/MATURITY_CRITERIA.md SHALL cobrir no mínimo os quatro eixos do caminho crítico: identidade de item sob reimportações reais, matching sob crescimento, revisão humana fechando o ciclo, ingestão real sem implodir premissas do domínio.
3. THE docs/MATURITY_CRITERIA.md SHALL indicar o status atual de cada critério (não provado, em progresso, provado).
4. WHEN um critério de maturidade é satisfeito, THE docs/MATURITY_CRITERIA.md SHALL ser atualizado para refletir o novo status.
5. THE docs/MATURITY_CRITERIA.md SHALL ser referenciado em docs/STATUS.md e em ANALISE_CONFORMIDADE.md como fonte de verdade sobre maturidade operacional.

### Requirement 5: Consistência entre documentos

**User Story:** Como agente ou colaborador que lê a documentação do repositório, quero que todos os documentos usem linguagem consistente sobre o estágio do projeto, para que não haja contradição entre arquivos.

#### Acceptance Criteria

1. THE repositório SHALL usar o termo "bootstrap funcional" (ou equivalente calibrado) de forma consistente em ANALISE_CONFORMIDADE.md, docs/STATUS.md e README.md.
2. IF um documento usa linguagem de produção ou maturidade operacional para descrever o estágio atual, THEN THE documento SHALL ser considerado não conforme com esta feature.
3. THE AGENTS.md SHALL ser verificado e, se necessário, atualizado para refletir a narrativa calibrada — especialmente a seção "Estado atual".
