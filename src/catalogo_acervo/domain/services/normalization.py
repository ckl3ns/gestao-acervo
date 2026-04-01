from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str | None) -> str | None:
    if text is None:
        return None

    normalized = unicodedata.normalize("NFKD", text)
    without_diacritics = "".join(char for char in normalized if not unicodedata.combining(char))
    collapsed = re.sub(r"\s+", " ", without_diacritics.strip().lower())
    return collapsed or None
