from __future__ import annotations

import re

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)

# Operadores booleanos FTS5 isolados (sem palavras ao redor)
_FTS5_BOOL_OPS = re.compile(r"\b(AND|OR|NOT)\b", re.IGNORECASE)
_FTS5_TOKEN_PATTERN = re.compile(r"[\w]+(?:-[\w]+)*")


def _sanitize_fts5_query(query: str) -> str:
    """Sanitiza query para uso seguro no SQLite FTS5.

    Estratégia defensiva: extrai tokens textuais simples e os quota
    individualmente antes de enviá-los ao FTS5. Isso impede que entradas do
    usuário sejam interpretadas como sintaxe especial de MATCH, inclusive em
    casos como ``0-0`` ou ``abc-def``.
    """
    if not query or not query.strip():
        return ""

    safe_tokens: list[str] = []
    for token in _FTS5_TOKEN_PATTERN.findall(query):
        if _FTS5_BOOL_OPS.fullmatch(token):
            continue
        escaped = token.replace('"', '""')
        safe_tokens.append(f'"{escaped}"')
    return " ".join(safe_tokens).strip()


class SearchCatalogUseCase:
    def __init__(self, repository: CatalogItemRepository) -> None:
        self.repository = repository

    def execute(self, query: str) -> list[CatalogItem]:
        sanitized = _sanitize_fts5_query(query)
        if not sanitized:
            return []
        return self.repository.search(sanitized)
