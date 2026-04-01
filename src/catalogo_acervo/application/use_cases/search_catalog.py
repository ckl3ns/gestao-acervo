from __future__ import annotations

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)


class SearchCatalogUseCase:
    def __init__(self, repository: CatalogItemRepository) -> None:
        self.repository = repository

    def execute(self, query: str) -> list[CatalogItem]:
        return self.repository.search(query)
