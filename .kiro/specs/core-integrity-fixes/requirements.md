# Documento de Requisitos — core-integrity-fixes

## Introdução

Uma revisão técnica rigorosa (pytest, ruff, mypy, testes dirigidos de comportamento) identificou 8 falhas estruturais no núcleo do sistema de catálogo unificado de acervo. Estas falhas não são problemas de acabamento: são falhas de semântica, integridade e verdade operacional que comprometem auditoria, idempotência, identidade de objetos, observabilidade, prioridade de regras, estabilidade da UI e governança de qualidade.

Este documento especifica os requisitos de correção para cada falha, em ordem de gravidade, com critérios de aceitação verificáveis.

---

## Glossário

- **ImportJob**: Entidade que representa uma execução de importação de arquivo para uma fonte. Campos: `import_mode`, `status`, `total_read`, `total_inserted`, `total_updated`, `total_skipped`, `total_errors`.
- **ImportRepository**: Repositório responsável por persistir e atualizar `ImportJob` no banco de dados.
- **Pipeline**: Sequência de operações executada pelo `ImportSourceItemsFromSourceUseCase` ao processar um arquivo de importação.
- **Upsert**: Operação de inserção ou atualização de um `CatalogItem` com base em `(source_id, source_key)`.
- **MatchRepository**: Repositório responsável por persistir pares de candidatos de matching na tabela `matches`.
- **SuggestMatchesUseCase**: Caso de uso que executa o algoritmo de matching entre itens do catálogo.
- **source_key**: Identificador estável de um item dentro de uma fonte, usado para preservar identidade entre reimportações.
- **AliasService**: Serviço de domínio (`apply_aliases`) responsável por substituir textos por suas formas canônicas.
- **AliasRepository**: Repositório que persiste e consulta aliases ativos.
- **FTS5**: Extensão de busca full-text do SQLite usada para indexar itens do catálogo.
- **SearchCatalogUseCase**: Caso de uso que executa buscas FTS5 sobre o catálogo.
- **mypy**: Verificador estático de tipos para Python.
- **ruff**: Linter e formatador de código Python.
- **ProcessingLogger**: Componente de logging estruturado de eventos do pipeline.

---

## Requisitos

---

### Requisito 1 — Semântica Verdadeira de Importação

**User Story:** Como auditor do sistema, quero que os contadores de importação (`total_inserted`, `total_updated`, `total_skipped`) reflitam o que realmente aconteceu no banco de dados, para que relatórios de importação sejam confiáveis e a trilha de auditoria não nasça corrompida.

**Contexto técnico:** `ImportJob.import_mode` nasce como `"full_replace"` mas o pipeline executa upsert incremental. `total_inserted` conta registros processados com sucesso, não linhas realmente inseridas. `total_updated` e `total_skipped` nunca são calculados — ficam sempre `0`. `ImportRepository.finish()` não recebe `total_updated` nem `total_skipped`.

#### Critérios de Aceitação

1. THE `ImportJob` SHALL ter `import_mode` com valor padrão `"upsert"`, refletindo a operação real executada pelo pipeline.
2. WHEN o `Pipeline` executa um upsert e o item já existe no banco com `(source_id, source_key)`, THE `Pipeline` SHALL incrementar `total_updated` em 1 para aquele `ImportJob`.
3. WHEN o `Pipeline` executa um upsert e o item não existe no banco, THE `Pipeline` SHALL incrementar `total_inserted` em 1 para aquele `ImportJob`.
4. WHEN o `Pipeline` decide não alterar um item por ausência de mudança detectável, THE `Pipeline` SHALL incrementar `total_skipped` em 1 para aquele `ImportJob`.
5. THE `ImportRepository.finish()` SHALL receber e persistir `total_updated` e `total_skipped` além dos campos já existentes.
6. WHEN uma importação é concluída, THE `ImportRepository` SHALL persistir `total_inserted`, `total_updated` e `total_skipped` com os valores reais calculados pelo `Pipeline`.
7. WHEN `total_inserted + total_updated + total_skipped + total_errors` é calculado após uma importação, THE resultado SHALL ser igual a `total_read`.

---

### Requisito 2 — Idempotência e Unicidade de Matching

**User Story:** Como operador do sistema, quero que reimportações não gerem pares de matching duplicados no banco de dados, para que o matching seja idempotente e o banco não acumule lixo entre execuções.

**Contexto técnico:** A tabela `matches` não possui constraint `UNIQUE(left_item_id, right_item_id)`. Cada reimportação insere novos registros duplicados para os mesmos pares. O algoritmo de matching faz varredura total O(n²) a cada execução, sem incrementalidade.

#### Critérios de Aceitação

1. THE `schema.sql` SHALL definir a constraint `UNIQUE(left_item_id, right_item_id)` na tabela `matches`.
2. WHEN o `MatchRepository` tenta inserir um par `(left_item_id, right_item_id)` que já existe, THE `MatchRepository` SHALL executar `INSERT OR IGNORE` ou `INSERT OR REPLACE`, sem lançar exceção e sem criar linha duplicada.
3. WHEN o `SuggestMatchesUseCase` é executado duas vezes consecutivas sem alteração nos dados, THE contagem de linhas na tabela `matches` SHALL ser igual antes e depois da segunda execução.
4. WHEN o `SuggestMatchesUseCase` é executado após uma reimportação que não alterou nenhum item, THE `SuggestMatchesUseCase` SHALL produzir zero novas linhas na tabela `matches`.
5. THE `SuggestMatchesUseCase` SHALL processar apenas pares que envolvam itens inseridos ou atualizados na importação corrente, evitando varredura total O(n²) a cada execução.

---

### Requisito 3 — Estabilidade de Identidade no Fallback de source_key

**User Story:** Como operador do sistema, quero que a identidade de um item seja preservada entre reimportações mesmo quando o arquivo fonte não possui chave estável, para que a ordem das linhas no arquivo não corrompa silenciosamente a identidade dos objetos.

**Contexto técnico:** O fallback atual usa `auto:{source_id}:{index}`, onde `index` é a posição da linha no arquivo. Inverter a ordem das linhas troca a identidade dos objetos, causando corrupção silenciosa entre reimportações.

#### Critérios de Aceitação

1. WHEN um registro não possui campo `source_key` nem campo `id`, THE `Pipeline` SHALL gerar um `source_key` de fallback baseado em um hash determinístico do conteúdo do registro, não na posição da linha.
2. WHEN dois registros com conteúdo idêntico são processados em ordens diferentes em execuções distintas, THE `source_key` gerado para cada registro SHALL ser o mesmo nas duas execuções.
3. WHEN um arquivo é reimportado com as linhas em ordem diferente, THE `Pipeline` SHALL preservar a identidade (`source_key`) de cada item, sem criar duplicatas nem trocar atributos entre itens distintos.
4. THE `Pipeline` SHALL registrar no `ProcessingLogger` quando o fallback de `source_key` é utilizado, incluindo o `source_id` e o hash gerado, para rastreabilidade.
5. IF dois registros distintos produzirem o mesmo hash de fallback, THEN THE `Pipeline` SHALL registrar colisão no `ProcessingLogger` e tratar o segundo registro como erro, incrementando `total_errors`.

---

### Requisito 4 — Proteção de Falha no Parser

**User Story:** Como operador do sistema, quero que uma falha no parser não deixe o ImportJob preso com status `"running"` para sempre, para que o banco permaneça consistente e a observabilidade não seja sabotada.

**Contexto técnico:** `parser.parse(file_path)` é chamado fora de qualquer bloco de proteção. Se o parser lança exceção, o job fica com `status="running"` indefinidamente, sem registro de erro.

#### Critérios de Aceitação

1. WHEN `parser.parse(file_path)` lança qualquer exceção, THE `Pipeline` SHALL capturar a exceção e chamar `ImportRepository.finish()` com `status="failed"` e `total_errors=1`.
2. WHEN o `Pipeline` finaliza um `ImportJob` com `status="failed"` por falha no parser, THE `ImportRepository` SHALL persistir o status `"failed"` no banco de dados.
3. IF `parser.parse(file_path)` lança exceção, THEN THE `Pipeline` SHALL registrar a exceção no `ProcessingLogger` com `level="ERROR"`, incluindo o nome do parser e o caminho do arquivo.
4. WHEN uma importação falha por erro no parser, THE `Pipeline` SHALL relançar a exceção após finalizar o `ImportJob`, para que o chamador seja notificado da falha.
5. THE `Pipeline` SHALL garantir que nenhum `ImportJob` permaneça com `status="running"` após o término da execução do método `execute()`, independentemente do tipo de falha ocorrida.

---

### Requisito 5 — Precedência Correta de Aliases por Especificidade

**User Story:** Como curador do catálogo, quero que aliases específicos de uma fonte tenham precedência sobre aliases globais do mesmo tipo, para que regras de escopo por fonte funcionem conforme esperado e não sejam silenciosamente ignoradas.

**Contexto técnico:** `apply_aliases()` itera sobre a lista de aliases sem garantia de que aliases com `source_scope` definido ganham dos aliases com `source_scope=None`. `AliasRepository.list_active()` ordena por `alias_kind, alias_text`, não por especificidade.

#### Critérios de Aceitação

1. THE `AliasRepository.list_active()` SHALL retornar aliases ordenados de forma que aliases com `source_scope` não-nulo precedam aliases com `source_scope=None` para o mesmo `alias_kind` e `alias_text`.
2. WHEN `apply_aliases()` encontra um alias com `source_scope` correspondente ao `source_scope` do item sendo processado, THE `AliasService` SHALL aplicar esse alias e não continuar iterando para aliases globais do mesmo tipo.
3. WHEN `apply_aliases()` não encontra alias específico para o `source_scope` do item, THE `AliasService` SHALL aplicar o alias global correspondente, se existir.
4. WHEN um alias global e um alias específico de fonte definem o mesmo `alias_text` para o mesmo `alias_kind`, THE `AliasService` SHALL aplicar o alias específico de fonte, ignorando o global.
5. THE `AliasService` SHALL produzir o mesmo resultado independentemente da ordem em que os aliases foram inseridos no banco de dados.

---

### Requisito 6 — Sanitização de Queries FTS5

**User Story:** Como usuário da interface, quero que a busca no catálogo não quebre com entradas comuns de texto livre, para que a UI não exiba erros operacionais causados por input normal.

**Contexto técnico:** `app/streamlit_app.py` passa a query do usuário diretamente ao `MATCH` do SQLite FTS5. Strings como `"unterminated"`, `"("`, `"C. J. Date"` causam `OperationalError`.

#### Critérios de Aceitação

1. THE `SearchCatalogUseCase` SHALL sanitizar a query recebida antes de passá-la ao FTS5, escapando ou removendo caracteres e tokens que causam `OperationalError` no SQLite FTS5.
2. WHEN o usuário fornece uma query com parênteses não balanceados, THE `SearchCatalogUseCase` SHALL retornar resultados válidos ou lista vazia, sem lançar exceção.
3. WHEN o usuário fornece uma query com caracteres especiais do FTS5 como `"`, `*`, `-`, `^`, THE `SearchCatalogUseCase` SHALL tratar esses caracteres de forma segura, sem lançar exceção.
4. WHEN o usuário fornece uma query vazia ou composta apenas de espaços, THE `SearchCatalogUseCase` SHALL retornar lista vazia sem lançar exceção.
5. IF a query sanitizada resultar em string vazia após remoção de tokens inválidos, THEN THE `SearchCatalogUseCase` SHALL retornar lista vazia sem executar query no banco de dados.
6. THE `SearchCatalogUseCase` SHALL preservar a intenção de busca do usuário ao sanitizar, removendo apenas os tokens que causariam erro, não a query inteira.

---

### Requisito 7 — Convergência entre Documentação e Comportamento Real

**User Story:** Como desenvolvedor do projeto, quero que `docs/STATUS.md` reflita o estado operacional real do sistema, para que a documentação não seja ficção administrativa e decisões técnicas sejam baseadas em fatos.

**Contexto técnico:** `docs/STATUS.md` afirma que "Matching integrado ao pipeline". `app/streamlit_app.py` instancia `ImportSourceItemsFromSourceUseCase` sem `SuggestMatchesUseCase`, tornando o matching inoperante na UI.

#### Critérios de Aceitação

1. WHEN `ImportSourceItemsFromSourceUseCase` é instanciado em `app/streamlit_app.py`, THE `App` SHALL passar uma instância de `SuggestMatchesUseCase` como argumento `suggest_matches_use_case`, tornando o matching operacional na UI.
2. THE `SuggestMatchesUseCase` instanciado na `App` SHALL receber um `MatchRepository` conectado ao banco de dados ativo da sessão.
3. WHEN `docs/STATUS.md` afirma que uma funcionalidade está "integrada" ou "funcional", THE documentação SHALL refletir o comportamento verificável no código de produção, não apenas a existência da implementação.
4. WHEN a integração de `SuggestMatchesUseCase` na UI for concluída, THE `docs/STATUS.md` SHALL ser atualizado para refletir o estado real, incluindo limitações conhecidas de escala.

---

### Requisito 8 — Governança Real de Qualidade de Código

**User Story:** Como desenvolvedor do projeto, quero que mypy, ruff e pytest governem efetivamente o código, para que ferramentas de qualidade instaladas não sejam decorativas e falhas de tipo sejam detectadas antes de chegar ao repositório.

**Contexto técnico:** `mypy src` falha com 10 erros básicos (dicts sem type args, `int | None` sem conversão segura). DTOs, mappers, `manual_review`, `match` e `processing_log` têm 0% de cobertura. O teste de integração de matching termina com `assert count >= 0`, que não testa nada.

#### Critérios de Aceitação

1. THE `Pipeline` SHALL passar em `mypy src` sem erros, com configuração `strict = false` e `disallow_untyped_defs = true`.
2. WHEN `mypy src` é executado, THE resultado SHALL ser zero erros de tipo nos módulos `domain`, `application` e `infrastructure`.
3. THE cobertura de testes dos módulos `interfaces/dto` e `interfaces/mappers` SHALL ser igual ou superior a 80%.
4. THE cobertura de testes dos módulos `domain/entities/manual_review`, `domain/entities/match` e `infrastructure/logging/processing_log` SHALL ser igual ou superior a 80%.
5. WHEN um teste de integração de matching é executado, THE teste SHALL verificar que o número de matches gerados é maior que zero para um conjunto de dados com itens sabidamente similares, não apenas que o valor é não-negativo.
6. THE teste de integração de matching SHALL verificar que pares específicos de itens com similaridade acima do limiar configurado estão presentes na tabela `matches` após a execução do `SuggestMatchesUseCase`.
7. THE configuração de `mypy` no `pyproject.toml` SHALL estar habilitada no hook `pre-push`, bloqueando commits que introduzam novos erros de tipo.
