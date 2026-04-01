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
        affected_set = set(affected_item_ids) if affected_item_ids is not None else None
        created = 0
        processed_pairs: set[tuple[int, int]] = set()

        for left in items:
            left_id = left.id
            if left_id is None:
                continue
            if affected_set is not None and left_id not in affected_set:
                continue

            for right in items:
                right_id = right.id
                if right_id is None:
                    continue
                if left_id == right_id or left.source_id == right.source_id:
                    continue

                pair = MatchRepository.canonicalize_pair(left_id, right_id)
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)

                match_result = suggest_match(left, right)
                if match_result.score < threshold:
                    continue

                band_value = match_result.band.value
                persisted_id = self.match_repo.add(
                    pair[0],
                    pair[1],
                    match_result.score,
                    match_result.rule,
                    "possible",
                    band_value,
                )
                if persisted_id is not None:
                    created += 1
        return created
