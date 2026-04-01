# Regras: Domínio e Arquitetura

> Carregado automaticamente pelo Claude Code a cada turno.

## Separação de camadas (inviolável)

```
app/           → PODE importar de application, infrastructure, config
               → NUNCA importa de domain diretamente (usar DTOs — WI-005)

application/   → PODE importar de domain, infrastructure
               → NUNCA importa de app/
               → NUNCA contém lógica de negócio (apenas orquestração)

domain/        → PODE importar apenas de domain
               → NUNCA importa de infrastructure, application, app
               → NUNCA importa sqlite3, streamlit, pydantic (exceto BaseModel)

infrastructure/→ PODE importar de domain
               → NUNCA importa de application, app
```

**Violação de camada = bug arquitetural, não de comportamento.** Reverta imediatamente.

## Entidades (domain/entities/)

- Sempre Pydantic `BaseModel`.
- IDs com `| None` para entidades ainda não persistidas.
- `created_at` e `updated_at` com `datetime | None` — preenchidos pelo banco.
- `raw_record_json: dict[str, Any]` para snapshot bruto do registro original.
- Nunca conter métodos de negócio — esses vão em `services/`.

## Value Objects (domain/value_objects/)

- Sempre `model_config = {"frozen": True}` — imutáveis.
- Validação completa no `@field_validator`.
- Factory method `@classmethod create(cls, ...)` para derivação automática de campos.
- Nunca expor construtor com estado inválido.

Exemplo correto:
```python
class MatchScore(BaseModel):
    score: float
    rule: str
    band: ConfidenceBand

    model_config = {"frozen": True}

    @field_validator("score")
    @classmethod
    def score_must_be_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError(f"score fora do range: {v}")
        return round(v, 2)

    @classmethod
    def create(cls, score: float, rule: str) -> "MatchScore":
        return cls(score=score, rule=rule, band=ConfidenceBand.from_score(score))
```

## Contracts (domain/contracts/)

- `Protocol` para inversão de dependência (não ABC).
- O Protocol define apenas os métodos que o use case precisa — mínimo viável.
- O repositório concreto implementa implicitamente (structural typing).

## Services (domain/services/)

- Funções puras sempre que possível.
- Sem estado interno.
- Sem dependência de banco, UI ou IO.
- Nomear como verbos: `normalize_text`, `apply_aliases`, `suggest_match`, `slugify_theme`.

## Parsers (infrastructure/ingestion/)

- Cada parser implementa `ParserContract` (`parse(file_path) -> list[dict]`).
- `parser_name: str` como atributo de classe (não de instância).
- Registrar via `ParserRegistry([ParserA(), ParserB()])`.
- Testar com arquivo real de fixtures — nunca mockar o parser.

```python
class LogosCsvParser(BaseParser):
    parser_name = "logos_csv"

    def parse(self, file_path: Path) -> list[dict]:
        ...
```

## Proibições

- Nunca criar dependência circular entre módulos.
- Nunca colocar lógica de negócio no Streamlit.
- Nunca colocar SQL no domínio.
- Nunca criar `utils.py` genérico — organizar por responsabilidade.
- Nunca introduzir LLM, embeddings, MCP operacional nesta fase (V0).
- Nunca introduzir autenticação, multiusuário, deploy cloud nesta fase.
