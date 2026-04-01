# Plano de Implementação — core-integrity-fixes

## Visão Geral

Correções cirúrgicas de 8 falhas estruturais no núcleo do sistema, executadas em ordem de gravidade e respeitando dependências entre arquivos. Cada task é atômica e referencia os requisitos correspondentes.

## Tasks

- [x] 1. Corrigir semântica verdadeira de importação
  - [x] 1.1 Alterar `ImportJob.import_mode` default para `"upsert"` em `domain/entities/import_job.py`
    - Trocar valor padrão de `"full_replace"` para `"upsert"`
    - _Requirements: 1.1_

  - [x] 1.2 Modificar `CatalogItemRepository.upsert()` para retornar `(item_id, operation)`
    - Adicionar `SELECT` de existência antes do upsert usando `UNIQUE(source_id, source_key)`
    - Comparar `raw_record_json` serializado para detectar `"skipped"`
    - Retornar `tuple[int, str]` com `"inserted"` | `"updated"` | `"skipped"`
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 1.3 Atualizar `ImportRepository.finish()` para receber e persistir `total_updated` e `total_skipped`
    - Adicionar parâmetros `total_updated: int` e `total_skipped: int` à assinatura
    - Atualizar query SQL para incluir esses campos
    - _Requirements: 1.5, 1.6_

  - [x] 1.4 Atualizar pipeline em `import_source_items_from_source.py` para separar contadores e acumular `affected_ids`
    - Substituir contador único por `inserted`, `updated`, `skipped`, `errors`
    - Acumular `affected_ids: list[int]` com IDs dos itens inseridos/atualizados
    - Passar todos os contadores para `import_repository.finish()`
    - _Requirements: 1.2, 1.3, 1.4, 1.6, 1.7_

  - [x] 1.5 Escrever testes unitários para semântica de importação
    - `test_import_job_default_mode`: verifica `import_mode == "upsert"`
    - `test_finish_persists_updated_skipped`: verifica persistência dos novos contadores
    - `test_counter_conservation`: verifica `inserted + updated + skipped + errors == total_read`
    - _Requirements: 1.1, 1.5, 1.7_

  - [x] 1.6 Escrever property test — Property 1: Invariante de conservação de contadores
    - **Property 1: counter conservation invariant**
    - **Validates: Requirements 1.7**
    - Usar `@given(st.lists(...))` com registros variados, verificar soma dos contadores

  - [x] 1.7 Escrever property test — Property 2: Corretude do contador de upsert
    - **Property 2: upsert counter correctness**
    - **Validates: Requirements 1.2, 1.3, 1.4**
    - Usar `@given(st.booleans())` para simular item existente vs. novo

- [x] 2. Adicionar proteção de falha no parser
  - Depende da task 1 (mesmo arquivo `import_source_items_from_source.py`)
  - [x] 2.1 Envolver `parser.parse(file_path)` em try/except com finalização garantida
    - Capturar qualquer exceção lançada pelo parser
    - Chamar `import_repository.finish()` com `status="failed"` e `total_errors=1`
    - Registrar no `ProcessingLogger` com `level="ERROR"`, nome do parser e caminho do arquivo
    - Re-lançar a exceção após finalizar o job
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 2.2 Escrever testes unitários para proteção do parser
    - `test_parser_failure_sets_failed_status`: mock parser que lança, verifica `status="failed"` no banco
    - `test_parser_failure_reraises`: verifica que a exceção é re-lançada após `finish()`
    - `test_no_job_stays_running_on_success`: verifica status final diferente de `"running"` em caso de sucesso
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

  - [x] 2.3 Escrever property test — Property 3: Nenhum ImportJob permanece com status "running"
    - **Property 3: no job stays running**
    - **Validates: Requirements 4.1, 4.2, 4.4, 4.5**
    - Usar `@given(st.booleans())` para simular parser falhando vs. sucesso

- [x] 3. Implementar fallback de source_key por hash determinístico
  - Depende da task 1 (mesmo arquivo `import_source_items_from_source.py`)
  - [x] 3.1 Substituir fallback `auto:{source_id}:{index}` por hash SHA-256 em `_extract_source_key()`
    - Usar `hashlib.sha256` sobre `json.dumps(record, sort_keys=True)`
    - Truncar digest para 16 caracteres, prefixar com `"hash:"`
    - Manter parâmetro `index` na assinatura para compatibilidade, mas não usá-lo no fallback
    - Registrar no `ProcessingLogger` quando fallback é acionado (source_id + hash gerado)
    - Tratar colisão de hash como erro: log + `total_errors++`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.2 Escrever testes unitários para fallback de source_key
    - `test_source_key_fallback_is_deterministic`: mesmo registro em ordens diferentes → mesmo hash
    - `test_source_key_fallback_prefix`: verifica prefixo `"hash:"`
    - `test_source_key_uses_explicit_field_when_present`: campo `id` ou `source_key` tem prioridade
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 3.3 Escrever property test — Property 6: Determinismo do source_key de fallback
    - **Property 6: source_key fallback determinism**
    - **Validates: Requirements 3.1, 3.2, 3.3**
    - Usar `@given(st.dictionaries(st.text(), st.text()))` e verificar resultado idêntico em qualquer ordem

- [x] 4. Checkpoint — Verificar tasks 1–3
  - Garantir que todos os testes das tasks 1, 2 e 3 passam antes de continuar.
  - Rodar `pytest -q` e confirmar zero falhas.

- [x] 5. Adicionar UNIQUE em matches e INSERT OR IGNORE no MatchRepository
  - [x] 5.1 Adicionar constraint `UNIQUE(left_item_id, right_item_id)` em `infrastructure/db/schema.sql`
    - Adicionar constraint na definição da tabela `matches`
    - Garantir que o bootstrap recria a tabela se necessário (DROP + CREATE ou migration)
    - _Requirements: 2.1_

  - [x] 5.2 Trocar `INSERT` por `INSERT OR IGNORE` em `MatchRepository.add()`
    - Atualizar query em `infrastructure/db/repositories/match_repository.py`
    - Garantir que nenhuma exceção é lançada em inserção duplicada
    - _Requirements: 2.2_

  - [x] 5.3 Escrever testes unitários para deduplicação de matches
    - `test_match_duplicate_insert_ignored`: inserir mesmo par duas vezes, verificar `count == 1`
    - `test_match_no_exception_on_duplicate`: verificar que não lança exceção
    - _Requirements: 2.1, 2.2_

  - [x] 5.4 Escrever property test — Property 5: Deduplicação de pares de matching
    - **Property 5: match deduplication**
    - **Validates: Requirements 2.1, 2.2**
    - Usar `@given(st.integers(min_value=1), st.integers(min_value=1))` e verificar sem duplicata

- [x] 6. Tornar SuggestMatchesUseCase incremental com affected_item_ids
  - Depende da task 1 (acumulação de `affected_ids` no pipeline) e task 5 (INSERT OR IGNORE)
  - [x] 6.1 Modificar `SuggestMatchesUseCase.execute()` para aceitar `affected_item_ids: list[int] | None`
    - Quando `affected_item_ids` é fornecido, filtrar `candidates` apenas para esses IDs
    - Quando `None`, manter comportamento atual (varredura total)
    - _Requirements: 2.5_

  - [x] 6.2 Passar `affected_ids` do pipeline para `SuggestMatchesUseCase.execute()`
    - Em `import_source_items_from_source.py`, chamar `suggest_matches_use_case.execute(affected_item_ids=affected_ids)`
    - _Requirements: 2.5_

  - [x] 6.3 Escrever testes unitários para incrementalidade do matching
    - `test_suggest_matches_incremental_only_processes_affected`: verifica que apenas IDs afetados são processados
    - `test_suggest_matches_idempotent_on_no_change`: segunda execução sem mudança não cria novas linhas
    - _Requirements: 2.3, 2.4, 2.5_

  - [x] 6.4 Escrever property test — Property 4: Idempotência do matching
    - **Property 4: match idempotence**
    - **Validates: Requirements 2.3, 2.4**
    - Usar estratégia de itens gerados, executar duas vezes, verificar contagem igual

- [x] 7. Corrigir precedência de aliases por especificidade
  - [x] 7.1 Atualizar `ORDER BY` em `AliasRepository.list_active()`
    - Adicionar `CASE WHEN source_scope IS NULL THEN 1 ELSE 0 END` como primeiro critério de ordenação
    - Aliases com `source_scope` não-nulo devem preceder aliases globais
    - _Requirements: 5.1_

  - [x] 7.2 Escrever testes unitários para precedência de aliases
    - `test_alias_scoped_wins_over_global`: alias específico e global para mesmo texto, verifica qual vence
    - `test_alias_global_used_when_no_scoped`: sem alias específico, global é aplicado
    - `test_alias_order_independent`: resultado igual independente da ordem de inserção
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 7.3 Escrever property test — Property 7: Precedência de alias específico sobre global
    - **Property 7: alias scoped precedence**
    - **Validates: Requirements 5.1, 5.2, 5.4, 5.5**
    - Usar `@given(st.text(), st.text(), st.text())` para alias_text, canonical global e scoped

- [x] 8. Sanitizar queries FTS5 em SearchCatalogUseCase
  - [x] 8.1 Implementar `_sanitize_fts5_query()` em `application/use_cases/search_catalog.py`
    - Remover aspas não fechadas
    - Remover parênteses não balanceados
    - Remover operadores FTS5 isolados (AND, OR, NOT no início/fim)
    - Remover `^` e `*` isolados sem palavra adjacente
    - Retornar string vazia se query for vazia ou só espaços
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 8.2 Aplicar sanitização em `SearchCatalogUseCase.execute()` antes de chamar o repositório
    - Retornar `[]` imediatamente se query sanitizada for vazia
    - _Requirements: 6.4, 6.5_

  - [x] 8.3 Escrever testes unitários para sanitização FTS5
    - `test_fts5_empty_query_returns_empty`: query vazia retorna lista vazia
    - `test_fts5_unbalanced_parens`: query `"(foo"` não lança exceção
    - `test_fts5_unclosed_quote`: query com aspas não fechadas não lança exceção
    - `test_fts5_isolated_operator`: query `"AND"` sozinha não lança exceção
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 8.4 Escrever property test — Property 8: Segurança de sanitização FTS5
    - **Property 8: FTS5 sanitization safety**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
    - Usar `@given(st.text())` com `max_examples=200`, verificar que nunca lança `OperationalError`

- [ ] 9. Wiring do matching na UI (streamlit_app.py)
  - [ ] 9.1 Importar `SuggestMatchesUseCase` e `MatchRepository` em `app/streamlit_app.py`
    - Adicionar imports necessários
    - _Requirements: 7.1, 7.2_

  - [ ] 9.2 Instanciar `MatchRepository` e `SuggestMatchesUseCase` na função de construção de use cases
    - Criar `match_repo = MatchRepository(conn)`
    - Criar `suggest_matches_uc = SuggestMatchesUseCase(items_repo=item_repo, match_repo=match_repo)`
    - Passar `suggest_matches_use_case=suggest_matches_uc` para `ImportSourceItemsFromSourceUseCase`
    - _Requirements: 7.1, 7.2_

  - [ ] 9.3 Escrever teste unitário para wiring da UI
    - `test_suggest_matches_wired_in_app`: instanciar use cases e verificar que `import_uc.suggest_matches_use_case` não é `None`
    - _Requirements: 7.1, 7.2_

- [ ] 10. Checkpoint — Verificar tasks 5–9
  - Garantir que todos os testes das tasks 5 a 9 passam antes de continuar.
  - Rodar `pytest -q` e confirmar zero falhas.

- [ ] 11. Corrigir erros mypy
  - [ ] 11.1 Executar `mypy src` e catalogar todos os erros atuais
    - Identificar arquivos com `dict` sem type args, `int | None` sem guard, funções sem anotação de retorno
    - _Requirements: 8.1, 8.2_

  - [ ] 11.2 Corrigir erros de tipo em `infrastructure/db/repositories/`
    - Substituir `dict` por `dict[str, Any]` ou tipo específico nos parâmetros SQL
    - Adicionar anotações de retorno faltantes
    - _Requirements: 8.1, 8.2_

  - [ ] 11.3 Corrigir erros de tipo em `application/use_cases/import_source_items_from_source.py`
    - Anotar `record: dict[str, Any]` e demais parâmetros sem type args
    - _Requirements: 8.1, 8.2_

  - [ ] 11.4 Corrigir erros de tipo em `domain/entities/`
    - Adicionar guards para campos `int | None` onde necessário
    - _Requirements: 8.1, 8.2_

  - [ ] 11.5 Configurar mypy em `pyproject.toml` com `strict = false` e `disallow_untyped_defs = true`
    - Adicionar seção `[tool.mypy]` se não existir
    - _Requirements: 8.1_

- [ ] 12. Escrever testes unitários para DTOs, mappers e entidades com baixa cobertura
  - [ ] 12.1 Escrever testes para `interfaces/dto/`
    - Cobrir criação, validação e serialização dos DTOs existentes
    - Atingir ≥ 80% de cobertura no módulo
    - _Requirements: 8.3_

  - [ ] 12.2 Escrever testes para `interfaces/mappers/`
    - Cobrir conversão entre entidades de domínio e DTOs
    - Atingir ≥ 80% de cobertura no módulo
    - _Requirements: 8.3_

  - [ ] 12.3 Escrever testes para `domain/entities/manual_review.py` e `domain/entities/match.py`
    - Cobrir criação de entidades, campos opcionais e validações
    - Atingir ≥ 80% de cobertura em cada módulo
    - _Requirements: 8.4_

  - [ ] 12.4 Escrever testes para `infrastructure/logging/processing_logger.py`
    - Cobrir registro de eventos com diferentes níveis e contextos
    - Atingir ≥ 80% de cobertura no módulo
    - _Requirements: 8.4_

  - [ ] 12.5 Corrigir teste de integração de matching para ter asserts reais
    - Substituir `assert count >= 0` por verificação de `count > 0` com dados sabidamente similares
    - Verificar que par específico de itens similares está presente na tabela `matches`
    - _Requirements: 8.5, 8.6_

- [ ] 13. Habilitar mypy no hook pre-push
  - [ ] 13.1 Atualizar `.githooks/pre-push` para executar `python -m mypy src` antes dos testes
    - Adicionar `python -m mypy src` com `set -e` para bloquear push em caso de erro
    - _Requirements: 8.7_

  - [ ] 13.2 Verificar que `make install-hooks` instala o hook atualizado corretamente
    - Confirmar que o script em `.githooks/pre-push` é executável e referenciado pelo Makefile
    - _Requirements: 8.7_

- [ ] 14. Checkpoint final — Garantir que todos os testes passam e mypy está limpo
  - Rodar `pytest -q` e confirmar zero falhas.
  - Rodar `mypy src` e confirmar zero erros.
  - Verificar cobertura dos módulos listados nos requisitos 8.3 e 8.4.

## Notas

- Tasks marcadas com `*` são opcionais e podem ser puladas para MVP mais rápido
- A ordem das tasks respeita dependências: tasks 2 e 3 dependem de 1 (mesmo arquivo); task 6 depende de 1 e 5
- Cada property test referencia explicitamente a propriedade do design document
- Testes de propriedade usam `hypothesis` com `@settings(max_examples=100)` (200 para Property 8)
- Cada task referencia os requisitos correspondentes para rastreabilidade
