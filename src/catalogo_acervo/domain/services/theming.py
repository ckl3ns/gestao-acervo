from __future__ import annotations

import re
import unicodedata


def slugify_theme(name: str) -> str:
    """Converte nome de tema em slug URL-safe.

    Ex: 'Teologia Bíblica' → 'teologia-biblica'
    """
    normalized = unicodedata.normalize("NFKD", name)
    without_diacritics = "".join(c for c in normalized if not unicodedata.combining(c))
    lowered = without_diacritics.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug
