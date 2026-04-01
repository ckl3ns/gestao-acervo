# PRD — Catálogo Unificado de Acervo Digital e Físico

## 1. Visão executiva

### 1.1 Nome do produto

Catálogo Unificado de Acervo

### 1.2 Problema real

O usuário possui acervos distribuídos em múltiplas fontes e formatos heterogêneos, com metadados inconsistentes e sem visão consolidada. Isso gera quatro perdas concretas:

* duplicidade de aquisição;
* dificuldade de localizar rapidamente se uma obra já existe;
* incapacidade de enxergar cobertura temática do acervo;
* inviabilidade prática de usar o acervo como base futura para assistentes de IA, recomendações e consultas inteligentes.

### 1.3 O que o produto deve ser

Um sistema local, modular e extensível para:

* importar inventários/catálogos/listagens de múltiplas fontes;
* normalizar e reconciliar metadados;
* organizar itens por grupos temáticos e fontes;
* permitir busca, comparação, filtros e revisão manual;
* servir como fundação futura para APIs e um servidor MCP.

### 1.4 O que o produto não deve ser na v1

* um chatbot;
* um RAG completo;
* uma plataforma colaborativa multiusuário;
* uma integração em tempo real com APIs oficiais externas;
* um sistema de compra automatizada.

---

## 2. Mudança de escopo confirmada

O projeto deixa de ser definido como “comparador Logos 7 × Accordance 14” e passa a ser definido como:

**um catálogo unificado e reconciliador de acervos, orientado por fontes, temas e uso futuro por IA.**

Essa mudança é obrigatória porque os exemplos já recebidos mostram naturezas distintas de fonte:

* catálogos estruturados de biblioteca digital, como Logos 7 e Logos 10, com campos bibliográficos relativamente tabulares fileciteturn5file0turn6file0
* exportações bibliográficas por registro, como Accordance 14 fileciteturn5file1
* estruturas curriculares/listas de cursos, como o Seminário Jonathan Edwards fileciteturn6file1
* diretórios de cursos em OneDrive/Zondervan com vídeos e guias PDF fileciteturn6file2
* inventários de PDFs acadêmicos por coleção/série, como LNTS/JSNTS fileciteturn6file3

Conclusão: o sistema precisa ser **source-agnostic**, com conectores/adaptadores por fonte.

---

## 3. Objetivo do produto

### 3.1 Objetivo principal

Permitir ao usuário saber, com alta confiança, se determinado recurso já existe em seu ecossistema pessoal de acervos, independentemente da fonte de origem.

### 3.2 Objetivos secundários

* consolidar diferentes bibliotecas e repositórios em um índice unificado;
* classificar o acervo por áreas temáticas, como Teologia, IA, Banco de Dados etc.;
* permitir atualização seletiva das fontes, mantendo apenas o estado atual do acervo;
* preparar a arquitetura para futura exposição via API e MCP;
* permitir futuras recomendações baseadas no acervo existente.

---

## 4. Visão de produto por fases

### Fase 1 — Catálogo unificado utilizável

* importação por arquivos;
* busca consolidada;
* comparação entre fontes;
* grupos temáticos;
* matching e revisão manual.

### Fase 2 — Consolidação operacional

* atualização seletiva por fonte;
* relatórios de cobertura temática;
* filtros avançados;
* regras/aliases administráveis.

### Fase 3 — Fundação de inteligência

* API interna estável;
* recomendações baseadas no acervo;
* análise de lacunas;
* prontidão para MCP.

### Fase 4 — Integração futura

* servidor MCP para consulta do acervo por modelos de IA;
* possíveis conectores adicionais (OneDrive, Google Drive, Calibre, pastas locais, outras bibliotecas digitais).

---

## 5. Personas

### 5.1 Persona principal

Pesquisador/estudioso com múltiplos acervos digitais e necessidade recorrente de verificar disponibilidade, redundância e cobertura temática.

### 5.2 Persona secundária

Usuário avançado que deseja transformar seu acervo pessoal em base estruturada para pesquisa, planejamento de aquisições, consulta temática e uso posterior com IA.

---

## 6. Escopo funcional macro

### 6.1 Fontes iniciais confirmadas

* Logos 7 fileciteturn5file0
* Logos 10 fileciteturn6file0
* Accordance 14 fileciteturn5file1
* Cursos do Seminário Teológico Jonathan Edwards fileciteturn6file1
* Cursos Zondervan / OneDrive fileciteturn6file2
* Listagens de séries acadêmicas/PDFs como LNTS/JSNTS fileciteturn6file3

### 6.2 Fontes futuras previstas

* OneDrive genérico
* Google Drive
* Calibre
* pastas locais indexadas
* outras bibliotecas/exportações textuais e CSV/JSON/XML quando viável

### 6.3 Domínios temáticos previstos

* Teologia
* IA
* Banco de Dados
* outras áreas definidas pelo usuário

---

## 7. Princípios de produto

1. **Local-first**: a v1 deve operar localmente, sem depender de serviços remotos.
2. **Extensível por adaptadores**: cada nova fonte entra por conector/parser próprio.
3. **Metadado bruto + normalizado**: nunca perder a origem original.
4. **Explicabilidade**: matching e classificação precisam ser auditáveis.
5. **Preparação para MCP**: arquitetura interna deve ser API-friendly, embora MCP não entre na v1.
6. **Estado atual, não histórico pesado**: manter snapshot atual por fonte, com reimportação e atualização seletiva.

---

## 8. Objetivos e não objetivos

### 8.1 Objetivos

* localizar uma obra por título, autor, série ou tema;
* identificar em quais fontes o item existe;
* classificar itens em grupos temáticos;
* atualizar uma fonte específica sem reconstruir tudo manualmente;
* permitir revisão manual de correspondências ambíguas;
* permitir futura exposição do catálogo para IA e MCP.

### 8.2 Não objetivos da v1

* recomendação automatizada avançada;
* dedução semântica por LLM;
* OCR pesado;
* sincronização bidirecional com provedores externos;
* edição rica de metadados em massa;
* notas pessoais por item.

---

## 9. Decisões de produto já tomadas

### 9.1 Escopo extensível por plataforma

Confirmado. O produto não será hardcoded para Logos/Accordance.

### 9.2 Aliases e overrides

Decisão: **incluir na v1 um módulo simples de aliases manuais editáveis**.

Justificativa: sem isso, a heterogeneidade entre fontes derruba a utilidade real do sistema. Isso não é “nice to have”; é mecanismo de sobrevivência do matching.

### 9.3 Histórico temporal

Decisão: **trabalhar com estado atual por fonte**, com atualização seletiva.

### 9.4 Notas pessoais

Decisão: **fora da v1**.

### 9.5 MCP futuro

Decisão: **planejar desde já a arquitetura para API e MCP**, mas não implementar MCP na v1.

### 9.6 Grupos temáticos

Decisão: **entrar já na v1**, em nível funcional mínimo.

---

## 10. Definição de domínio

### 10.1 Entidades centrais

* Fonte
* Item do acervo
* Grupo temático
* Alias
* Match
* Revisão manual
* Importação
* Log de processamento

### 10.2 Tipos de item previstos

* livro/monografia
* comentário bíblico
* dicionário/enciclopédia
* gramática
* curso
* vídeo de curso
* PDF acadêmico
* coleção/série
* outro recurso bibliográfico/didático

### 10.3 Relações principais

* uma fonte possui muitos itens;
* um item pode pertencer a múltiplos grupos temáticos;
* um item pode corresponder a item(s) de outra fonte;
* um alias pode afetar título, autor, série, editora ou grupo temático.

---

## 11. Casos de uso prioritários

1. Verificar se um livro já existe em qualquer uma das bibliotecas indexadas.
2. Descobrir se o mesmo título existe em mais de uma plataforma.
3. Filtrar o acervo por grupo temático, como Teologia ou IA.
4. Verificar cobertura de uma série ou coleção.
5. Reprocessar apenas uma fonte específica após atualização do inventário.
6. Revisar matches incertos sugeridos pelo sistema.
7. Listar itens exclusivos por fonte.
8. Localizar cursos e materiais acadêmicos associados a uma área.
9. Preparar a base para futuras consultas via IA do tipo “já tenho algo sobre Teologia Joanina?”

---

## 12. Requisitos funcionais

### RF-01 — Cadastro de fontes

O sistema deve registrar e diferenciar fontes distintas, com tipo, nome, parser e configuração mínima.

### RF-02 — Importação por fonte

O usuário deve poder importar arquivos de uma fonte específica.

### RF-03 — Atualização seletiva

O usuário deve poder reimportar apenas uma fonte e atualizar seu estado atual.

### RF-04 — Persistência do bruto

Todo registro importado deve preservar seu conteúdo bruto.

### RF-05 — Normalização

O sistema deve gerar representações normalizadas para campos relevantes.

### RF-06 — Busca global

O usuário deve poder consultar por texto livre em todo o catálogo unificado.

### RF-07 — Filtros

O usuário deve poder filtrar por fonte, tipo, idioma, autor, série, ano, grupo temático e status de correspondência.

### RF-08 — Matching interfontes

O sistema deve sugerir correspondências entre itens de fontes distintas.

### RF-09 — Revisão manual

O usuário deve poder confirmar ou rejeitar matches sugeridos.

### RF-10 — Aliases

O usuário deve poder criar aliases simples para corrigir ou consolidar metadados recorrentes.

### RF-11 — Grupos temáticos

O usuário deve poder classificar itens em grupos temáticos.

### RF-12 — Classificação automática inicial

O sistema deve permitir regras iniciais simples para sugerir grupo temático com base em fonte, pasta, série, palavras-chave ou tipo.

### RF-13 — Dashboard

O sistema deve exibir visão consolidada do acervo por fontes, tipos e temas.

### RF-14 — Exportação

O sistema deve exportar listas filtradas em CSV.

### RF-15 — API interna preparada

O sistema deve ter camada de serviço desacoplada da interface, permitindo exposição futura por API.

---

## 13. Requisitos não funcionais

### RNF-01 — Arquitetura modular

Parsers, normalização, matching, classificação temática e interface devem ser desacoplados.

### RNF-02 — Local-first

A operação principal deve funcionar localmente em Windows.

### RNF-03 — Persistência simples

Banco local SQLite na v1.

### RNF-04 — Escalabilidade funcional

A adição de nova fonte não deve exigir reescrita do núcleo do sistema.

### RNF-05 — Auditabilidade

Toda decisão relevante de matching deve ser explicável e rastreável.

### RNF-06 — Prontidão para migração futura

O desenho deve permitir migração posterior de SQLite para Postgres, caso seja publicado remotamente.

### RNF-07 — Prontidão para MCP

O domínio e os serviços devem ser organizados para futura exposição por ferramentas/recursos MCP.

---

## 14. Regras de negócio

### RB-01

Cada item pertence a exatamente uma fonte de origem.

### RB-02

Um item pode pertencer a zero, um ou múltiplos grupos temáticos.

### RB-03

Somente itens de fontes diferentes podem formar correspondência interfonte.

### RB-04

Confirmações e rejeições manuais prevalecem sobre o algoritmo.

### RB-05

O sistema armazena o estado atual por fonte; reimportações atualizam esse estado.

### RB-06

Não haverá, na v1, histórico temporal completo de snapshots.

### RB-07

Um item pode existir no catálogo sem qualquer correspondência encontrada.

### RB-08

Aliases manuais podem alterar a interpretação normalizada, mas não o metadado bruto original.

---

## 15. Estratégia de classificação temática

### 15.1 Objetivo

Permitir organização do acervo em áreas, começando por Teologia e deixando pronto para expansão.

### 15.2 Modelo

Os grupos temáticos serão tratados como taxonomia flexível.

### 15.3 Exemplos iniciais

* Teologia
* IA
* Banco de Dados
* Filosofia
* História
* Ciências Bíblicas
* Linguagens Bíblicas
* Cursos

### 15.4 Abordagem v1

* grupos cadastráveis;
* associação manual por item;
* regras simples de sugestão por fonte, pasta, série, palavras-chave e tipo.

### 15.5 Abordagem futura

* classificação assistida por modelos;
* sugestões automáticas baseadas em corpus e metadados.

---

## 16. Estratégia de matching

### 16.1 Princípio

Priorizar precisão e explicabilidade. Nada de magia estatística cedo demais.

### 16.2 Camadas

1. Match exato por chave canônica relevante.
2. Match por título + autor.
3. Match por título + série/volume.
4. Match por título + ano/editora compatíveis.
5. Match fuzzy com limiar conservador.
6. Aplicação de aliases.
7. Aplicação de decisões manuais.

### 16.3 Classificações

* confirmado automático
* possível correspondência
* confirmado manualmente
* rejeitado manualmente
* sem correspondência

---

## 17. Estratégia de atualização das fontes

### 17.1 Estado atual

O sistema manterá uma visão atual do catálogo por fonte.

### 17.2 Atualização seletiva

O usuário poderá reimportar uma única fonte.

### 17.3 Comportamento esperado

* inserir itens novos;
* atualizar itens alterados quando a chave de origem permitir;
* desativar ou marcar como ausentes itens que deixem de existir, se a política da fonte assim exigir;
* preservar decisões manuais sempre que possível.

### 17.4 Política inicial

Na v1, o sistema deve ser conservador: atualizar o necessário sem destruir vínculos manuais existentes sem confirmação.

---

## 18. Modelo conceitual de dados

### 18.1 Tabela `sources`

* id
* name
* source_type
* parser_name
* description
* is_active
* created_at
* updated_at

### 18.2 Tabela `imports`

* id
* source_id
* import_mode
* imported_at
* status
* total_read
* total_inserted
* total_updated
* total_skipped
* total_errors
* raw_file_name

### 18.3 Tabela `catalog_items`

* id
* source_id
* source_key
* item_type
* title_raw
* title_norm
* subtitle_raw
* author_raw
* author_norm
* series_raw
* series_norm
* publisher_raw
* publisher_norm
* year
* language
* volume
* edition
* path_or_location
* resource_type
* raw_record_json
* is_active
* current_import_id
* created_at
* updated_at

### 18.4 Tabela `matches`

* id
* left_item_id
* right_item_id
* match_score
* match_rule
* status
* confidence_band
* created_at
* updated_at

### 18.5 Tabela `manual_reviews`

* id
* left_item_id
* right_item_id
* decision
* note
* created_at
* updated_at

### 18.6 Tabela `aliases`

* id
* alias_kind
* alias_text
* canonical_text
* source_scope
* is_active
* created_at
* updated_at

### 18.7 Tabela `themes`

* id
* name
* slug
* description
* created_at
* updated_at

### 18.8 Tabela `item_themes`

* id
* item_id
* theme_id
* assignment_type
* created_at
* updated_at

### 18.9 Tabela `processing_logs`

* id
* source_id
* import_id
* level
* message
* context_json
* created_at

---

## 19. Arquitetura proposta

### 19.1 Stack recomendada para v1

* Python
* Streamlit
* SQLite
* SQLite FTS5
* RapidFuzz
* Pydantic
* Pytest

### 19.2 Arquitetura lógica

1. **Camada de interface** — Streamlit
2. **Camada de aplicação** — casos de uso
3. **Camada de domínio** — matching, normalização, classificação temática, regras
4. **Camada de persistência** — repositórios
5. **Camada de ingestão** — parsers/adaptadores por fonte

### 19.3 Decisão crítica

A camada de domínio não pode depender da interface. Essa separação é o que permitirá API futura e MCP sem reescrever o núcleo.

---

## 20. Estratégia para MCP futuro

### 20.1 Meta

Permitir, no futuro, perguntas como:

* “já tenho algo forte sobre Teologia Joanina?”
* “tenho obra suficiente sobre apologética ou vale comprar mais?”
* “quais recursos do meu acervo poderiam me ajudar com uma disciplina específica?”

### 20.2 Implicações arquiteturais já na v1

* serviços internos devem ser organizados como casos de uso independentes;
* consultas principais devem poder ser expostas como funções ferramentalizáveis;
* busca, filtros e recomendações futuras devem usar uma camada de serviço estável;
* o catálogo deve ser semanticamente rico o suficiente para suportar perguntas futuras.

### 20.3 Fora da v1

* servidor MCP efetivo;
* recomendação por LLM;
* embeddings;
* inferência semântica avançada.

---

## 21. UX / módulos de interface

### 21.1 Dashboard

* total de itens por fonte;
* total por tema;
* itens exclusivos por fonte;
* pendências de revisão manual;
* últimos imports.

### 21.2 Busca global

* caixa única de busca;
* filtros por fonte, tema, tipo, idioma, autor, série e status.

### 21.3 Tela de comparação

* metadados lado a lado;
* score;
* regra;
* decisão manual.

### 21.4 Tela de importação

* upload/seleção do arquivo;
* escolha/validação da fonte;
* reprocessamento seletivo;
* resumo do resultado.

### 21.5 Tela de aliases

* listar aliases;
* criar/editar/desativar;
* definir escopo.

### 21.6 Tela de temas

* listar grupos temáticos;
* criar/editar;
* associar itens manualmente;
* revisar sugestões automáticas simples.

---

## 22. Critérios de aceite por épico

### Épico 1 — Núcleo do catálogo

* O sistema cadastra fontes.
* O sistema persiste itens de fontes distintas com identidade preservada.

### Épico 2 — Ingestão por adaptadores

* Cada parser inicial funciona para seu formato conhecido.
* Falhas de parsing são registradas sem derrubar a importação inteira.

### Épico 3 — Busca unificada

* O usuário encontra itens por texto livre em todo o catálogo.
* O usuário consegue restringir por tema e fonte.

### Épico 4 — Matching

* O sistema identifica correspondências úteis entre fontes.
* Casos ambíguos podem ser revistos manualmente.

### Épico 5 — Temas

* O usuário consegue criar grupos temáticos.
* O usuário consegue associar itens a esses grupos.

### Épico 6 — Atualização seletiva

* O usuário consegue atualizar apenas uma fonte.
* O sistema preserva dados essenciais e decisões manuais.

---

## 23. Roadmap realista

### Fase 0 — Fundamentos

* congelar domínio e arquitetura;
* criar schema;
* criar camada de fonte/adaptador.

### Fase 1 — MVP funcional

* Logos 7
* Logos 10
* Accordance 14
* busca global
* matching básico
* aliases básicos
* temas básicos

### Fase 2 — Expansão inicial

* Jonathan Edwards
* Zondervan
* LNTS/JSNTS
* atualização seletiva
* dashboard e relatórios

### Fase 3 — Consolidação

* refino de matching
* regras de classificação temática
* exportações
* API interna mais madura

### Fase 4 — Preparação IA/MCP

* endpoints/serviços para consulta estruturada
* avaliação de API pública/local
* desenho do servidor MCP

---

## 24. Backlog priorizado

### Must have

* modelo de fontes
* parser/adaptador por fonte inicial
* catálogo unificado
* normalização
* busca global
* matching interfontes
* revisão manual
* grupos temáticos
* aliases editáveis
* atualização seletiva

### Should have

* dashboard consolidado
* relatórios CSV
* classificação temática sugerida por regras
* logs melhores

### Could have

* conectores OneDrive/Google Drive/Calibre
* recomendação simples baseada em cobertura
* API HTTP local

### Won’t have now

* MCP operacional
* recomendação por LLM
* multiusuário completo
* sincronização automática com lojas

---

## 25. Riscos

### R-01 — Explosão de escopo

Mitigação: manter v1 local, sem IA, sem MCP, sem colaboração.

### R-02 — Parsers frágeis

Mitigação: fixtures reais e testes por fonte.

### R-03 — Taxonomia temática virar bagunça

Mitigação: começar simples, com grupos controlados.

### R-04 — Matching ruim entre fontes muito diferentes

Mitigação: aliases + revisão manual + thresholds conservadores.

### R-05 — Querer publicar cedo demais

Mitigação: validar utilidade local antes de qualquer deploy sério.

---

## 26. Decisão sobre Heroku

### 26.1 Veredito

**Não usar Heroku como premissa da v1.**

### 26.2 Motivo

A v1 é local-first, com SQLite e ingestão por arquivos. Publicação remota cedo demais adiciona complexidade e não resolve o núcleo do problema.

### 26.3 Uso futuro possível

Se o produto amadurecer para interface remota/API, Heroku pode servir com migração para Postgres. Não é prioridade agora.

---

## 27. Estratégia de testes

### Unitários

* normalização
* aliases
* extração por parser
* matching
* classificação temática por regra

### Integração

* importação por fonte
* atualização seletiva
* persistência de revisões e aliases

### Aceitação

* cenários reais com os arquivos já fornecidos pelo usuário

---

## 28. Métricas de sucesso

* redução drástica do tempo para verificar se um recurso já existe;
* baixa taxa de falso positivo em matches confirmados;
* uso efetivo dos grupos temáticos;
* reimportação seletiva sem perda de confiança;
* prontidão arquitetural para API/MCP sem retrabalho estrutural.

---

## 29. Questões em aberto remanescentes

As respostas recebidas já fecharam quase tudo. Restam apenas decisões operacionais futuras, não bloqueios de produto.

---

## 30. Recomendação executiva final

O produto correto não é um “comparador de duas bibliotecas”.

É um **núcleo pessoal de inventário bibliográfico e educacional**, com reconciliação de fontes, organização temática e preparo para consulta inteligente futura.

Essa é a fundação certa. Todo o resto — API, MCP, recomendações, conectores externos — vem depois.