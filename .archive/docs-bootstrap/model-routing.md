# Model Routing Guide

> Finalidade: definir uma política objetiva de escolha de modelos para planejamento, execução, revisão e tarefas auxiliares.
> 
> Este documento existe para reduzir improviso, evitar desperdício de capacidade premium e padronizar o uso dos modelos disponíveis em diferentes providers.

---

## 1. Princípios

### 1.1 Escolher por perfil cognitivo da tarefa, não por provider
A escolha do modelo deve ser feita pela natureza do trabalho:
- triagem
- planejamento
- execução
- revisão
- documentação

O mesmo modelo pode aparecer em múltiplos ambientes. O provider muda; o papel operacional do modelo não.

### 1.2 Separar planejamento, execução e revisão
Planejar, implementar e revisar são trabalhos diferentes. O processo deve preferir:
- modelo forte para planejar problemas difíceis;
- modelo eficiente para executar o volume do backlog;
- modelo crítico para revisão de risco.

### 1.3 Preservar modelos premium para tarefas premium
Modelos de custo alto ou disponibilidade mais restrita não devem ser usados em tarefas pequenas, repetitivas ou locais.

### 1.4 Registrar o modelo utilizado
Toda tarefa relevante deve registrar em `docs/WORK_ITEMS.md`:
- modelo principal utilizado;
- fallback usado, se houver;
- motivo da escolha, quando a tarefa for complexa.

---

## 2. Categorias de trabalho

### 2.1 Triagem
Usada para:
- decompor uma demanda crua;
- gerar checklist inicial;
- organizar ideias;
- fazer resumo rápido;
- filtrar se a tarefa é simples ou complexa.

### 2.2 Planning
Usado para:
- quebrar épicos em tarefas;
- comparar alternativas;
- analisar trade-offs;
- planejar arquitetura;
- definir ordem de implementação.

### 2.3 Execução
Usado para:
- escrever código;
- refatorar;
- criar e ajustar testes;
- implementar backlog;
- modificar o repositório com impacto real.

### 2.4 Revisão
Usado para:
- encontrar riscos;
- criticar a abordagem;
- revisar diffs grandes;
- detectar falhas de lógica;
- checar se a implementação atende ao objetivo.

### 2.5 Trabalho braçal / apoio
Usado para:
- documentação;
- logs;
- templates;
- rascunhos de testes;
- transformação de texto.

---

## 3. Matriz de roteamento por modelo

| Modelo / família | Papel principal | Considerar quando... | Evitar quando... |
|---|---|---|---|
| **Gemini 3 Flash** | Triagem rápida | checklist, rascunho técnico, refactor pequeno, revisão rápida de arquivo, decomposição inicial | arquitetura crítica, bug profundo, refactor perigoso, decisão estrutural |
| **Gemini 3 Pro** | Planning e análise | quebra de épicos, trade-offs, arquitetura, análise de diff grande, revisão conceitual, task design | tarefa trivial/local ou trabalho mecânico de baixo valor |
| **Gemini Thinking / Thinking with Pro** | Planning textual fora do repo | roadmap, backlog, comparação de abordagens, análise de alternativas, refinement | operação direta no repositório, tarefas que exigem execução no workspace |
| **GPT-5 mini** | Tarefa miúda / copiloto | autocomplete, helpers, testes simples, boilerplate, markdown curto, ajustes locais | arquitetura, debugging difícil, refactor grande, tarefa ambígua e longa |
| **GPT-5.3-Codex** | Execução agentic séria | tarefas longas no repo, terminal, testes, pesquisa, implementação end-to-end, worktree isolada | microtarefas ou brainstorming cru |
| **Claude Haiku** | Filtro rápido | resumo, reescrita simples, triagem rápida, pequenas transformações | planejamento sério, revisão crítica, bug difícil |
| **Claude Sonnet** | Generalista equilibrado | coding geral, revisão boa sem custo extremo, tarefas médias, especificações razoáveis | casos realmente difíceis onde Opus é melhor, ou tarefas tão simples que mini/Flash bastam |
| **Claude Opus** | Revisão crítica de elite | arquitetura de risco alto, bug infernal, revisão adversarial, PR grande, destruição de plano fraco | rotina de implementação, tarefas simples, ajustes locais |
| **Claude `opusplan`** | Planejar + executar | quando a tarefa precisa de planning forte antes da implementação e o fluxo está no Claude Code | tarefas simples ou contextos sem Claude Code |
| **MiniMax M2.7** | Cavalo de batalha de execução | implementação normal de backlog, refactor médio, debugging normal, testes, volume contínuo de trabalho | decisões arquiteturais muito críticas sem segunda opinião, revisão adversarial pesada |

---

## 4. Estratégia recomendada do projeto

### 4.1 Modelo principal por função

#### Triagem
1. **Gemini 3 Flash**
2. **GPT-5 mini**
3. **Claude Haiku**

#### Planning
1. **Gemini 3 Pro**
2. **Claude `opusplan`**
3. **Claude Opus**

#### Execução padrão do backlog
1. **MiniMax M2.7**
2. **GPT-5.3-Codex**
3. **Claude Sonnet**

#### Revisão pesada
1. **Claude Opus**
2. **Gemini 3 Pro**
3. **GPT-5.3-Codex**

#### Tarefas simples e locais
1. **GPT-5 mini**
2. **Gemini 3 Flash**
3. **Claude Haiku**

---

## 5. Regras de escalonamento

### 5.1 Comece barato quando o problema for simples
Se a tarefa:
- cabe em um arquivo;
- não mexe em arquitetura;
- não envolve risco alto;
- não exige múltiplos passos;

então começar com modelo premium é desperdício.

### 5.2 Escale quando houver sinais de falha
Troque de modelo quando ocorrer qualquer um dos seguintes:
- resposta instável entre tentativas;
- plano inconsistente;
- dificuldade para manter contexto da tarefa;
- solução superficial para problema estrutural;
- falhas repetidas nos testes sem progresso real.

### 5.3 Use revisão forte em mudanças de alto impacto
Toda mudança que altere:
- arquitetura;
- schema;
- workflow do repositório;
- hooks;
- automação;
- políticas do processo;

deveria passar por um modelo de revisão mais forte, preferencialmente **Claude Opus** ou **Gemini 3 Pro**.

---

## 6. Padrões de uso por cenário

### 6.1 Criar uma tarefa a partir de uma ideia crua
- Use **Gemini 3 Flash** para triagem inicial.
- Se a tarefa tiver risco estrutural, replaneje com **Gemini 3 Pro**.

### 6.2 Quebrar um épico em tarefas executáveis
- Use **Gemini 3 Pro**.
- Se o desenho for muito sensível, peça crítica de **Claude Opus**.

### 6.3 Implementar uma feature normal
- Use **MiniMax M2.7** como executor principal.
- Use **GPT-5 mini** para apoio local.
- Escale para **GPT-5.3-Codex** se a tarefa exigir execução agentic mais forte.

### 6.4 Refactor grande e perigoso
- Planeje com **Gemini 3 Pro**.
- Execute com **MiniMax M2.7** ou **GPT-5.3-Codex**.
- Revise com **Claude Opus**.

### 6.5 Revisar um PR grande
- Use **Claude Opus** como revisor principal.
- Use **Gemini 3 Pro** como segundo parecer se necessário.

### 6.6 Documentação, status, progresso e arquivos markdown
- Use **Gemini 3 Flash** ou **GPT-5 mini** para primeira passada.
- Escale para **Gemini 3 Pro** se o documento for normativo, estratégico ou afetar o processo.

---

## 7. Regras de registro no repositório

Toda tarefa deve registrar:
- `task_id`;
- modelo principal;
- fallback, se usado;
- branch;
- worktree;
- status (`backlog`, `in-progress`, `blocked`, `done`);
- testes executados.

Campos mínimos recomendados em `docs/WORK_ITEMS.md`:
- task id
- título
- responsável/agente
- modelo principal
- fallback
- branch
- worktree
- status
- started at
- finished at
- commits
- tests

---

## 8. Regras do que não fazer

### 8.1 Não usar modelo premium por impulso
Evitar usar **Claude Opus** ou **GPT-5.3-Codex** para:
- funções pequenas;
- boilerplate;
- pequenos ajustes em markdown;
- reescritas triviais;
- mudanças que não merecem análise profunda.

### 8.2 Não usar modelo leve em problema estrutural
Evitar usar **GPT-5 mini**, **Gemini 3 Flash** ou **Claude Haiku** como modelo principal para:
- arquitetura;
- bugs sistêmicos;
- mudanças multiarquivo com risco alto;
- revisão de processo;
- decisões de design duradouras.

### 8.3 Não mandar a mesma tarefa para vários modelos sem papel definido
Paralelismo sem papéis claros gera conflito, ruído e retrabalho.

---

## 9. Heurística rápida de escolha

Use esta regra mental:

- **Isso é triagem?** → Gemini 3 Flash
- **Isso é planejamento?** → Gemini 3 Pro
- **Isso é implementação rotineira?** → MiniMax M2.7
- **Isso é microtarefa no editor?** → GPT-5 mini
- **Isso é execução agentic séria?** → GPT-5.3-Codex
- **Isso é revisão crítica de risco alto?** → Claude Opus
- **Isso é pensar + executar no fluxo Claude?** → Claude `opusplan`

---

## 10. Decisão normativa atual do projeto

Até nova revisão, o projeto adota a seguinte política:

1. **Gemini 3 Pro** é o modelo preferencial de **planning**.
2. **MiniMax M2.7** é o modelo preferencial de **execução contínua do backlog**.
3. **GPT-5 mini** é o modelo preferencial de **tarefas corriqueiras e locais**.
4. **Claude Opus** é o modelo preferencial de **revisão crítica e análise pesada**.
5. **GPT-5.3-Codex** é o modelo preferencial para **execução agentic séria no repositório**.
6. **Gemini 3 Flash** é o modelo preferencial de **triagem e decomposição rápida**.
7. Toda exceção deve ser justificada na tarefa quando a mudança for estrutural ou de alto risco.

---

## 11. Quando revisar este documento

Revisar este documento quando houver qualquer uma das seguintes mudanças:
- entrada de um novo provider ou modelo relevante;
- mudança de disponibilidade/custo dos modelos;
- percepção recorrente de falha em uma rota de uso;
- alteração significativa na natureza do projeto;
- mudança na estratégia de execução multiagente.

---

## 12. Última observação

Este documento não existe para idolatrar modelos. Existe para impedir improviso.

A pergunta correta não é:
> “qual modelo é melhor?”

A pergunta correta é:
> “qual modelo é mais adequado para este tipo específico de trabalho, neste momento, com este custo e este risco?”

