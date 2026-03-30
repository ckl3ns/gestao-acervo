from __future__ import annotations

from catalogo_acervo.domain.services.matching import suggest_match
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import CatalogItemRepository
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository


class SuggestMatchesUseCase:
    def __init__(self, items_repo: CatalogItemRepository, match_repo: MatchRepository) -> None:
        self.items_repo = items_repo
        self.match_repo = match_repo

    def execute(self, threshold: float = 85.0) -> int:
        items = self.items_repo.list_all()
        created = 0
        for i, left in enumerate(items):
            for right in items[i + 1 :]:
                if left.source_id == right.source_id:
                    continue
                score, rule = suggest_match(left, right)
                if score >= threshold:
                    band = "high" if score >= 92 else "medium"
                    self.match_repo.add(left.id or 0, right.id or 0, score, rule, "possible", band)
                    created += 1
        return created
