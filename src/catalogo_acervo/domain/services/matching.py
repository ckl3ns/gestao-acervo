from __future__ import annotations

from rapidfuzz import fuzz

from catalogo_acervo.domain.entities.catalog_item import CatalogItem


def suggest_match(item_a: CatalogItem, item_b: CatalogItem) -> tuple[float, str]:
    title_score = fuzz.token_set_ratio(item_a.title_norm or "", item_b.title_norm or "")
    author_score = fuzz.token_set_ratio(item_a.author_norm or "", item_b.author_norm or "")
    final_score = (title_score * 0.7) + (author_score * 0.3)
    rule = "title+author_fuzzy"
    return round(final_score, 2), rule
