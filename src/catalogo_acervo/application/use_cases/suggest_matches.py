from __future__ import annotations

from catalogo_acervo.domain.services.matching import suggest_match
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.match_repository import MatchRepository


class SuggestMatchesUseCase:
    def __init__(self, items_repo: CatalogItemRepository, match_repo: MatchRepository) -> None:
        self.items_repo = items_repo
        self.match_repo = match_repo

    def execute(self, threshold: float = 85.0, affected_item_ids: list[int] | None = None) -> int:
        items = self.items_repo.list_all()
        if affected_item_ids is not None:
            affected_set = set(affected_item_ids)
            candidates = [i for i in items if i.id in affected_set]
        else:
            candidates = items
        created = 0
        for left in candidates:
            for right in items:
                if left.id == right.id or left.source_id == right.source_id:
                    continue
                match_result = suggest_match(left, right)
                if match_result.score >= threshold:
                    band_value = match_result.band.value
                    self.match_repo.add(
                        left.id or 0, right.id or 0, match_result.score, match_result.rule, "possible", band_value
                    )
                    created += 1
        return created
