# INSTRUCTIONS.md

Este repositório é operado por agentes de IA sob coordenação humana.
O mantenedor atua como **PO/cliente**. A coordenação técnica e de processo deve ser assumida por um agente com postura de **Scrum Master + Tech Lead Sênior**. Os demais agentes atuam como equipe de desenvolvimento.

Este arquivo define as regras obrigatórias de execução.

## 1. Objetivo do projeto
Construir um **catálogo unificado de acervo digital e físico**, local-first, preparado para múltiplas fontes, múltiplos temas e evolução futura para API/MCP.

O foco atual não é IA conversacional, deploy ou UI sofisticada.
O foco atual é o **núcleo confiável**:
- ingestão por fonte;
- normalização;
- aliases;
- atualização seletiva por fonte;
- matching;
- revisão manual;
- rastreabilidade de mudanças.

## 2. Papéis e responsabilidades

### PO / cliente
Responsável por:
- definir prioridade;
- validar entregas;
- aprovar merges;
- arbitrar escopo.

### Scrum Master / Tech Lead
Responsável por:
- quebrar trabalho em unidades pequenas e verificáveis;
- impor disciplina de branch, commit, testes e documentação;
- evitar deriva de escopo;
- garantir qualidade mínima de código e markdown;
- registrar progresso, decisões e pendências.

### Agentes executores
Responsáveis por:
- ler os arquivos de governança antes de qualquer alteração;
- atuar em worktree/branch isolada por grande tarefa;
- manter commits pequenos e semânticos;
- rodar testes antes de cada commit;
- atualizar os arquivos de progresso;
- não fazer merge em `main`.

## 3. Arquivos que TODO agente deve ler antes de trabalhar
Ordem obrigatória:
1. `INSTRUCTIONS.md`
2. `AGENTS.md`
3. `docs/STATUS.md`
4. `docs/WORK_ITEMS.md`
5. `docs/workflow.md`
6. `README.md`
7. `docs/architecture.md`
8. `docs/decisions.md`
9. `docs/MATURITY_CRITERIA.md`

Nenhum agente deve iniciar trabalho sem ler esses arquivos.

## 4. Regras operacionais obrigatórias

### 4.1 Unidade de trabalho
- Uma **grande tarefa** = uma branch + uma worktree dedicada.
- Um **commit** = uma mudança semanticamente isolada.
- Não misturar correção, refatoração, documentação e UI no mesmo commit sem necessidade extrema.

### 4.2 Commits
- Commits devem ser pequenos, reversíveis e semanticamente claros.
- Padrões aceitos:
  - `feat(...)`
  - `fix(...)`
  - `refactor(...)`
  - `test(...)`
  - `docs(...)`
  - `chore(...)`
- Exemplos:
  - `fix(normalization): fold diacritics in canonical text`
  - `feat(app): wire source-driven imports`
  - `docs(governance): define multi-agent workflow`

### 4.3 Testes antes de commit
- **É proibido commitar com testes falhando.**
- O hook de pre-commit deve bloquear o commit se os testes falharem.
- O agente deve rodar `pytest -q` conscientemente antes do commit, mesmo com hook instalado.

### 4.4 Progresso e status
Toda ação relevante deve ser refletida na documentação de progresso:
- atualizar `docs/STATUS.md`;
- atualizar `docs/WORK_ITEMS.md`;
- registrar branch, commit, data e status da tarefa.

### 4.5 Integração com `main`
- Nada vai para `main` sem testes verdes.
- Nada vai para `main` sem revisão humana.
- Nada vai para `main` se a branch estiver misturando escopos.

## 5. Regras de isolamento com worktrees
Cada nova grande tarefa deve usar worktree própria.

Padrão sugerido:
- branch: `agent/<tema-curto>` ou `assistant/<tema-curto>` ou `codex/<tema-curto>`
- worktree: `../wt-<tema-curto>`

Exemplo:
```bash
git worktree add ../wt-update-selective-sync -b assistant/update-selective-sync
```

Regras:
- uma worktree por grande tarefa;
- não reutilizar worktree para tarefa diferente;
- encerrar e remover a worktree quando a tarefa acabar;
- registrar a worktree e a branch em `docs/WORK_ITEMS.md`.

## 6. Qualidade mínima obrigatória

### Código
- nomes explícitos;
- funções e classes pequenas;
- sem código morto novo;
- sem comentários redundantes;
- sem acoplamento desnecessário com UI;
- testes cobrindo comportamento novo ou alterado.

### Markdown
- sem texto vago;
- sem instruções contraditórias;
- sem arquivo “bonito porém inútil”;
- toda documentação deve servir a operação do repositório.

## 7. Restrições de escopo
Enquanto o núcleo não estiver consistente, evitar:
- chatbot;
- embeddings;
- MCP operacional;
- deploy;
- autenticação complexa;
- UI sofisticada;
- integrações externas amplas.

Prioridade do backlog:
1. atualização seletiva por fonte;
2. matching;
3. revisão manual;
4. auditoria e operação mínima útil;
5. somente depois IA/MCP/deploy.

## 8. Definição de pronto para cada tarefa
Uma tarefa só é considerada pronta quando:
- tem branch própria;
- tem commits semânticos;
- tem testes verdes;
- tem progresso documentado;
- tem pendências explícitas;
- está pronta para PR sem esconder risco estrutural.

## 9. Handoff entre agentes
Todo handoff deve registrar:
- branch;
- worktree;
- tarefa;
- status atual;
- últimos commits;
- testes executados;
- próximos passos;
- riscos conhecidos.

Registrar isso em `docs/WORK_ITEMS.md` e, se necessário, em `docs/STATUS.md`.

## 10. Regra final
Se a mudança parecer conveniente, mas não aproximar o núcleo do objetivo real, ela deve ser adiada.
