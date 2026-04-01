# Regras: Padrões de Teste

> Carregado automaticamente pelo Claude Code a cada turno.

## Filosofia

- Todo comportamento novo = teste novo. Sem exceção.
- Testar comportamento, não implementação.
- Casos de borda > caminho feliz. O caminho feliz já foi provado pelos testes existentes.
- Cada anti-padrão documentado em CLAUDE.md seção 6 deve ter pelo menos um teste de regressão.

## Fixtures obrigatórias (conftest.py)

```python
# Usar sempre estas fixtures — nunca recriar setup manualmente
db_conn              # SQLite :memory: com schema completo + PRAGMA FK ON
source_repo          # SourceRepository(db_conn)
source_lookup        # SourceLookupRepository(db_conn)
alias_repo           # AliasRepository(db_conn)
item_repo            # CatalogItemRepository(db_conn)
import_repo          # ImportRepository(db_conn)
logger               # ProcessingLogger(db_conn)
parser_registry      # ParserRegistry([MockParser()])
registered_source_id # INSERT mínimo em sources, retorna id (satisfaz FK)
```

**Nunca usar `tmp_path` para banco** — usar `db_conn` do conftest (SQLite in-memory é mais rápido e mais limpo).

## Estrutura de teste

```python
def test_<comportamento>_<condição>(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """Uma frase descrevendo o que está sendo testado e por quê."""
    # Arrange
    item = CatalogItem(source_id=registered_source_id, ...)
    
    # Act
    item_repo.upsert(item)
    
    # Assert
    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.year == 2020
```

## Nomenclatura de testes

- Formato: `test_<o_que_faz>_<condição_ou_input>`
- Exemplos:
  - `test_upsert_preserves_year_when_new_is_none`
  - `test_extract_source_key_falls_back_to_auto_when_no_id`
  - `test_confidence_band_returns_high_above_90`

## Testes parametrizados

Usar `@pytest.mark.parametrize` para múltiplos inputs do mesmo comportamento:

```python
@pytest.mark.parametrize(("score", "expected"), [
    (100.0, ConfidenceBand.HIGH),
    (90.0,  ConfidenceBand.HIGH),
    (89.9,  ConfidenceBand.MEDIUM),
    (0.0,   ConfidenceBand.REJECTED),
])
def test_confidence_band_thresholds(score, expected):
    assert ConfidenceBand.from_score(score) == expected
```

## Testes de integração

- Sempre usar o pipeline completo: RegisterSource → Import → Search.
- Testar o FTS5 explicitamente após upsert com conflito.
- Testar aliases aplicados na normalização.
- Arquivo de dados: `data/samples/mock_source.csv` (3 linhas, suficiente para maioria dos testes).

## Proibições

- Nunca mockar o banco — testar contra SQLite in-memory real.
- Nunca usar `time.sleep()`.
- Nunca `pytest.raises(Exception)` genérico — usar tipo específico.
- Nunca `# pragma: no cover` em código novo sem justificativa.
- Nunca commitar com testes falhando.
- Nunca commitar com cobertura abaixo de 70%.
