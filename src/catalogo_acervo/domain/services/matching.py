from __future__ import annotations

from rapidfuzz import fuzz

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.domain.value_objects.match_score import MatchScore

_RULE_TITLE_AUTHOR = "title+author_fuzzy"
_WEIGHT_TITLE = 0.7
_WEIGHT_AUTHOR = 0.3


def suggest_match(item_a: CatalogItem, item_b: CatalogItem) -> MatchScore:
    """Compara dois itens e retorna um MatchScore tipado.

    Algoritmo: média ponderada título (70%) + autor (30%) via token_set_ratio.
    token_set_ratio é robusto a reordenação de palavras e prefixos parciais,
    o que é adequado para títulos e nomes de autores em acervos heterogêneos.
    """
    title_score = fuzz.token_set_ratio(item_a.title_norm or "", item_b.title_norm or "")
    author_score = fuzz.token_set_ratio(item_a.author_norm or "", item_b.author_norm or "")
    final = (title_score * _WEIGHT_TITLE) + (author_score * _WEIGHT_AUTHOR)
    return MatchScore.create(score=final, rule=_RULE_TITLE_AUTHOR)
