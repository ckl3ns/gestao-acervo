from __future__ import annotations


def slugify_theme(name: str) -> str:
    return "-".join(name.strip().lower().split())
