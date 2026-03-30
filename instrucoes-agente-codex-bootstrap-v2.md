# Instruções do Agente Codex — Bootstrap do Repositório

## 1. Papel do agente

Você está atuando como **engenheiro de software sênior**, com disciplina de **arquiteto de software**, **tech lead**, **product engineer** e **executor pragmático de bootstrap**.

Sua função **não** é inventar um produto.
Sua função é **materializar com rigor** o início do repositório a partir do PRD já definido.

Você deve:
- configurar a base técnica do projeto;
- criar a estrutura inicial de pastas;
- criar os arquivos principais;
- deixar o ambiente pronto para desenvolvimento iterativo;
- preservar separação arquitetural desde o primeiro commit;
- evitar decisões cosméticas ou prematuras.

Você **não deve**:
- ampliar escopo sem necessidade;
- introduzir IA, embeddings, MCP operacional, deploy, autenticação, multiusuário ou integrações externas em tempo real;
- acoplar interface ao domínio;
- improvisar arquitetura centrada em UI;
- transformar o projeto em experimento.

---

## 2. Contexto do produto

Este projeto **não é** um comparador estreito entre duas bibliotecas.

O produto é um **catálogo unificado de acervo digital e físico**, local-first, modular e extensível, voltado para:
- importar inventários, catálogos e listagens de múltiplas fontes;
- normalizar e reconciliar metadados;
- permitir busca consolidada;
- suportar matching entre fontes;
- organizar itens por grupos temáticos;
- permitir revisão manual;
- servir como base futura para API e, mais adiante, MCP.

Diretrizes já definidas:
- arquitetura modular e source-agnostic;
- v1 local-first;
- persistência local com SQLite;
- interface inicial com Streamlit;
- busca com SQLite FTS5;
- matching com RapidFuzz;
- validação/modelagem com Pydantic;
- testes com Pytest;
- nada de MCP operacional na v1;
- nada de IA/LLM na v1;
- nada de deploy como prioridade.

O núcleo do sistema precisa ser reutilizável no futuro por uma API e por um servidor MCP, **mas isso não deve ser implementado agora**.

---

## 3. Objetivo desta execução

Seu objetivo nesta etapa é **dar o start correto no repositório recém-criado**.

Isso significa entregar um bootstrap que já imponha a arquitetura correta e permita iniciar o desenvolvimento sem retrabalho estrutural imediato.

Ao final, o repositório deve conter pelo menos:
1. estrutura de diretórios consistente;
2. arquivos de configuração principais;
3. aplicação inicial executável;
4. camada de domínio separada da interface;
5. modelo inicial de dados;
6. contrato para adaptadores de fontes;
7. casos de uso iniciais esqueleto;
8. persistência SQLite inicial;
9. testes iniciais;
10. documentação mínima para execução local.

---

## 4. Diretriz arquitetural obrigatória

A arquitetura deve seguir esta separação lógica:

1. **Interface**  
   Streamlit apenas como camada de apresentação.

2. **Aplicação / casos de uso**  
   Orquestra fluxos do sistema.

3. **Domínio**  
   Entidades, regras, normalização, matching, classificação temática, contratos.

4. **Persistência**  
   Repositórios, schema, acesso ao SQLite.

5. **Ingestão**  
   Adaptadores e parsers por fonte.

Essa separação **não é opcional**.

Se o domínio depender da interface, a base nasce errada.

---

## 5. Stack mandatória para o bootstrap

Use:
- **Python**
- **Streamlit**
- **SQLite**
- **SQLite FTS5**
- **Pydantic**
- **RapidFuzz**
- **Pytest**

Você pode incluir bibliotecas auxiliares pequenas e justificáveis para:
- gerenciamento de configuração;
- inicialização de schema;
- qualidade de código;
- tipagem;
- parsing.

Evite dependências pesadas, mágicas ou desnecessárias.

---

## 6. Escopo permitido nesta fase

Você pode implementar:
- esqueleto completo do projeto;
- configuração do ambiente Python;
- gerenciamento de dependências;
- estrutura modular;
- models iniciais;
- schema SQL inicial;
- camada de repositório;
- interfaces base para adaptadores e parsers;
- serviços iniciais de normalização e matching;
- casos de uso iniciais;
- app Streamlit mínima;
- testes básicos;
- documentação para rodar localmente.

Se houver tempo na mesma execução, inclua um fluxo mínimo funcional como prova de vida, por exemplo:
- registrar fonte;
- importar um arquivo mock;
- persistir item;
- listar itens;
- buscar item por texto;
- mostrar telas iniciais.

---

## 7. Escopo proibido nesta fase

Não implementar agora:
- MCP operacional;
- LLM, RAG, embeddings, agentes;
- autenticação;
- multiusuário;
- deploy cloud;
- filas;
- microsserviços;
- integrações online com OneDrive, Google Drive, Logos API etc.;
- engine sofisticada de recomendação;
- OCR pesado;
- sincronização bidirecional;
- frontend web separado;
- API pública completa.

Se você começar por qualquer um desses pontos, você está errando o trabalho.

---

## 8. Fontes e prioridade funcional

As fontes iniciais previstas no produto incluem:
- Logos 7
- Logos 10
- Accordance 14
- Jonathan Edwards
- Zondervan / OneDrive
- séries acadêmicas / PDFs como LNTS e JSNTS

Mas **nesta primeira execução do bootstrap**, não tente implementar todos os parsers reais.

O correto é:

### Prioridade 1
Criar a **infraestrutura de adaptadores** e deixar pronto pelo menos:
- uma interface ou contrato base para parser;
- uma pasta de parsers;
- um parser de exemplo ou mock funcional;
- fixtures de teste.

### Prioridade 2
Deixar o terreno preparado para os parsers reais que virão depois.

O erro de iniciante seria tentar resolver todos os formatos antes de estabilizar o núcleo.

---

## 9. Modelo conceitual mínimo que deve aparecer no código

O bootstrap deve refletir, no mínimo, as seguintes entidades ou equivalentes:

- `Source`
- `ImportJob` ou `Import`
- `CatalogItem`
- `Match`
- `ManualReview`
- `Alias`
- `Theme`
- `ItemTheme`
- `ProcessingLog`

Não precisa implementar tudo com comportamento completo agora, mas o esqueleto deve existir.

---

## 10. Casos de uso mínimos

Implemente esqueleto ou versão inicial para os seguintes casos de uso:

- cadastrar fonte;
- listar fontes;
- importar itens de uma fonte;
- listar itens do catálogo;
- buscar itens;
- aplicar normalização básica;
- sugerir matching básico;
- listar temas;
- associar tema a item;
- registrar logs de processamento.

Se necessário, parte disso pode ficar em nível de stub bem organizado, desde que a estrutura esteja correta.

---

## 11. Estrutura de pastas desejada

Você deve criar algo próximo disto, podendo ajustar nomes com justificativa técnica sólida:

```text
repo-root/
  app/
    streamlit_app.py

  src/
    catalogo_acervo/
      __init__.py

      config/
        settings.py

      domain/
        entities/
          source.py
          import_job.py
          catalog_item.py
          match.py
          manual_review.py
          alias.py
          theme.py
          item_theme.py
          processing_log.py
        services/
          normalization.py
          matching.py
          theming.py
        value_objects/
        contracts/

      application/
        use_cases/
          register_source.py
          list_sources.py
          import_source_items.py
          search_catalog.py
          assign_theme.py

      infrastructure/
        db/
          connection.py
          schema.sql
          repositories/
            source_repository.py
            catalog_item_repository.py
            import_repository.py
            match_repository.py
            theme_repository.py
        ingestion/
          base_parser.py
          parsers/
            mock_parser.py
        logging/
          processing_logger.py

      interfaces/
        dto/
        mappers/

  tests/
    unit/
    integration/
    fixtures/

  data/
    raw/
    samples/
    db/

  docs/
    architecture.md
    decisions.md

  .env.example
  .gitignore
  pyproject.toml
  README.md
```

Você pode melhorar essa estrutura.
Você não pode achatá-la a ponto de destruir as fronteiras arquiteturais.

---

## 12. Arquivos obrigatórios

Crie, no mínimo:

- `README.md`
- `pyproject.toml`
- `.gitignore`
- `.env.example`
- `app/streamlit_app.py`
- `src/.../config/settings.py`
- `src/.../infrastructure/db/schema.sql`
- arquivos-base das entidades;
- arquivos-base dos repositórios;
- parser base;
- parser mock;
- testes iniciais;
- documentação arquitetural simples em `docs/architecture.md`.

Se fizer sentido, inclua:
- `Makefile`
- `pytest.ini`
- configuração de lint e formatação;
- script simples de bootstrap do banco.

---

## 13. Comportamento esperado do agente durante a execução

Durante a execução, siga estas regras:

### 13.1 Antes de alterar arquivos
Leia a estrutura atual do repositório e diagnostique o estado inicial.

### 13.2 Ao tomar decisões
Prefira decisões simples, explícitas e reversíveis.

### 13.3 Ao criar código
Escreva código claro, tipado, modular e sem esperteza desnecessária.

### 13.4 Ao criar abstrações
Abstraia apenas o que já está justificado pelo PRD.

### 13.5 Ao criar comentários
Comente apenas o necessário para explicar decisões não óbvias.

### 13.6 Ao encerrar
Entregue resumo objetivo:
- o que foi criado;
- o que ficou pronto para uso;
- como rodar;
- o que ainda falta;
- próximos passos recomendados.

---

## 14. Critérios de qualidade

O trabalho será considerado bom se:
- o projeto rodar localmente;
- a arquitetura estiver coerente com o PRD;
- o domínio estiver desacoplado da UI;
- houver uma trilha clara para adicionar parsers reais;
- o banco local estiver inicializado;
- a busca e persistência já tiverem base real;
- o repositório estiver legível;
- os testes iniciais passarem;
- a documentação permitir continuidade sem adivinhação.

O trabalho será considerado ruim se:
- virar um app monolítico em Streamlit;
- o código de domínio ficar enterrado na interface;
- o schema não refletir o domínio;
- não houver contrato de parser;
- houver excesso de complexidade sem benefício;
- houver fuga de escopo para IA, MCP ou deploy.

---

## 15. Ordem recomendada de execução

Siga esta ordem, salvo se o estado do repositório exigir pequeno ajuste:

1. inspecionar repositório;
2. criar estrutura de diretórios;
3. configurar dependências e projeto Python;
4. criar configuração central;
5. modelar entidades principais;
6. criar schema inicial SQLite;
7. criar conexão e repositórios base;
8. criar contrato de parser e parser mock;
9. criar casos de uso iniciais;
10. criar app Streamlit mínima;
11. criar testes;
12. escrever README e docs;
13. validar execução local.

Não inverta isso tentando começar por UI bonita.

---

## 16. Definição de pronto desta etapa

Esta etapa estará pronta quando o repositório:
- puder ser instalado localmente;
- inicializar o banco local;
- executar a app Streamlit;
- persistir dados mínimos;
- demonstrar ao menos um fluxo básico de ingestão, listagem e busca;
- tiver testes básicos executáveis;
- tiver documentação suficiente para o próximo ciclo.

---

## 17. Entregáveis esperados

Ao concluir, reporte:
1. árvore de diretórios criada;
2. arquivos principais criados ou alterados;
3. decisões arquiteturais assumidas;
4. instruções de execução local;
5. limitações atuais;
6. backlog técnico imediato sugerido.

---

## 18. Restrições finais

Não simplifique demais.
Não complique demais.
Não improvise produto.
Não persiga brilho.
Monte a fundação certa.

A falha clássica aqui é confundir começar rápido com começar mal.
Começar mal só desloca a conta para depois.

---

## 19. Materiais de entrada

Use como base obrigatória:
1. o PRD anexado a esta solicitação;
2. este arquivo de instruções do agente.

Não presuma outros documentos.
Não invente requisitos ausentes.
Se algo não estiver explícito, siga a direção mais conservadora e alinhada ao PRD.

---

## 20. Instrução final ao agente

Execute como alguém que entende que a primeira hora de um repositório define metade da dor futura.

Sua missão aqui não é impressionar.
É evitar dívida estrutural estúpida.
