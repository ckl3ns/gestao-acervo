from __future__ import annotations

import re

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)

# Operadores booleanos FTS5 isolados (sem palavras ao redor)
_FTS5_BOOL_OPS = re.compile(r'\b(AND|OR|NOT)\b', re.IGNORECASE)


def _sanitize_fts5_query(query: str) -> str:
    """Sanitiza query para uso seguro no SQLite FTS5.

    Estratégia defensiva: extrai apenas palavras alfanuméricas (e hífens
    internos), descartando qualquer caractere que o FTS5 possa interpretar
    como operador ou delimitador especial. Isso garante que nenhuma entrada
    do usuário cause OperationalError, ao custo de não suportar sintaxe FTS5
    avançada via UI.
    """
    if not query or not query.strip():
        return ""

    # Extrair apenas tokens de palavra (letras, dígitos, underscore, hífen interno)
    words = re.findall(r'\b[\w][\w\-]*\b', query)
    # Remover operadores booleanos isolados
    words = [w for w in words if not _FTS5_BOOL_OPS.fullmatch(w)]
    return ' '.join(words).strip()


class SearchCatalogUseCase:
    def __init__(self, repository: CatalogItemRepository) -> None:
        self.repository = repository

    def execute(self, query: str) -> list[CatalogItem]:
        sanitized = _sanitize_fts5_query(query)
        if not sanitized:
            return []
        return self.repository.search(sanitized)
