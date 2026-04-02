from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser

_REQUIRED_COLUMNS = {
    "Resource ID",
    "Title",
    "Logos Title",
    "Resource Type",
    "Authors",
    "Series",
    "Languages",
    "Metadata Language",
    "Publication Date",
    "Electronic Publication Date",
    "File Name",
}

_RESOURCE_TYPE_MAP = {
    "Monografia": "book",
    "Comentário": "commentary",
    "Comentário bíblico": "commentary",
    "Bíblia": "bible",
    "Léxico": "lexicon",
    "Enciclopédia": "dictionary",
    "Revista": "journal",
    "Diário": "journal",
    "Sermões": "sermon",
    "Estudo Bíblico": "study_guide",
    "Devocional agendado": "devotional",
}

_YEAR_PATTERN = re.compile(r"(1[0-9]{3}|20[0-9]{2})")


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _parse_year(*candidates: str | None) -> int | None:
    for candidate in candidates:
        text = _clean(candidate)
        if text is None:
            continue
        match = _YEAR_PATTERN.search(text)
        if match is None:
            continue
        year = int(match.group(1))
        if 1000 <= year <= 2100:
            return year
    return None


def _map_item_type(resource_type: str | None) -> str:
    normalized = _clean(resource_type)
    if normalized is None:
        return "other"
    return _RESOURCE_TYPE_MAP.get(normalized, "other")


class LogosCsvParser(BaseParser):
    """Parser para exportações CSV da biblioteca do Logos 7 e Logos 10."""

    parser_name = "logos_csv"

    def parse(self, file_path: Path) -> list[dict[str, Any]]:
        with file_path.open("r", encoding="utf-8-sig", newline="") as fp:
            reader = csv.DictReader(fp)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                raise ValueError("CSV Logos sem cabeçalho")
            missing = sorted(_REQUIRED_COLUMNS.difference(fieldnames))
            if missing:
                missing_cols = ", ".join(missing)
                raise ValueError(f"CSV Logos inválido. Colunas obrigatórias ausentes: {missing_cols}")

            rows: list[dict[str, Any]] = []
            for raw_row in reader:
                rows.append(self._normalize_row(raw_row))
            return rows

    @staticmethod
    def _normalize_row(raw_row: dict[str, str | None]) -> dict[str, Any]:
        resource_id = _clean(raw_row.get("Resource ID"))
        if resource_id is None:
            raise ValueError("Registro Logos sem Resource ID")

        title = _clean(raw_row.get("Title")) or _clean(raw_row.get("Logos Title"))
        if title is None:
            raise ValueError(f"Registro Logos sem título (resource_id={resource_id})")

        normalized: dict[str, Any] = {key: _clean(value) for key, value in raw_row.items()}
        normalized.update(
            {
                "source_key": resource_id,
                "title": title,
                "author": _clean(raw_row.get("Authors")),
                "series": _clean(raw_row.get("Series")),
                "publisher": _clean(raw_row.get("Publishers")),
                "year": _parse_year(
                    raw_row.get("Publication Date"),
                    raw_row.get("Electronic Publication Date"),
                ),
                "language": _clean(raw_row.get("Languages")) or _clean(raw_row.get("Metadata Language")),
                "item_type": _map_item_type(raw_row.get("Resource Type")),
                "resource_type": _clean(raw_row.get("Resource Type")),
                "path_or_location": _clean(raw_row.get("File Name")),
            }
        )
        return normalized
