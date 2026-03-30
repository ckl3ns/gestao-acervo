from __future__ import annotations

import re


def normalize_text(text: str | None) -> str | None:
    if text is None:
        return None
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return normalized or None
