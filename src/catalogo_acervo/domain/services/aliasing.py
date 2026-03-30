from __future__ import annotations

from catalogo_acervo.domain.entities.alias import Alias
from catalogo_acervo.domain.services.normalization import normalize_text


ALIAS_KINDS = {"title", "author", "series", "publisher"}


def apply_aliases(
    text: str | None,
    *,
    alias_kind: str,
    aliases: list[Alias],
    source_scope: str | None = None,
) -> str | None:
    normalized = normalize_text(text)
    if normalized is None:
        return None

    if alias_kind not in ALIAS_KINDS:
        raise ValueError(f"alias_kind inválido: {alias_kind}")

    for alias in aliases:
        if alias.alias_kind != alias_kind:
            continue
        if not alias.is_active:
            continue
        if alias.source_scope not in (None, source_scope):
            continue
        if normalize_text(alias.alias_text) == normalized:
            return normalize_text(alias.canonical_text)

    return normalized
