from __future__ import annotations

from pathlib import Path

from catalogo_acervo.infrastructure.ingestion.parsers.logos_csv_parser import (
    LogosCsvParser,
    _map_item_type,
    _parse_year,
)

_LOGOS10_SAMPLE = Path("data/samples/logos10_sample.csv")
_LOGOS7_SAMPLE = Path("data/samples/logos7_sample.csv")


def test_parse_logos10_csv_maps_core_fields() -> None:
    parser = LogosCsvParser()

    rows = parser.parse(_LOGOS10_SAMPLE)

    assert len(rows) == 3
    first = rows[0]
    assert first["source_key"] == "LLS:FDNMRTLDDDLM"
    assert first["title"] == "Fedão (a imortalidade da alma)"
    assert first["author"] == "Platão"
    assert first["publisher"] == "Faithlife"
    assert first["year"] == 2021
    assert first["language"] == "português"
    assert first["item_type"] == "book"
    assert first["resource_type"] == "Monografia"
    assert first["path_or_location"] == "FDNMRTLDDDLM.logos4"


def test_parse_logos7_csv_accepts_schema_without_publishers() -> None:
    parser = LogosCsvParser()

    rows = parser.parse(_LOGOS7_SAMPLE)

    assert len(rows) == 3
    first = rows[0]
    assert first["source_key"] == "LLS:NIDOTTE"
    assert first["title"] == "New International Dictionary of Old Testament Theology and Exegesis"
    assert first["author"] == "VanGemeren, Willem A."
    assert first["publisher"] is None
    assert first["year"] == 1997
    assert first["language"] == "inglês"
    assert first["item_type"] == "lexicon"
    assert first["resource_type"] == "Léxico"
    assert first["path_or_location"] == "NIDOTTE.logos4"


def test_parse_year_accepts_ranges_and_rejects_invalid_values() -> None:
    assert _parse_year("1908-1914") == 1908
    assert _parse_year("1925-1976") == 1925
    assert _parse_year("n.d.") is None
    assert _parse_year("20204") == 2020


def test_map_item_type_falls_back_to_other_for_unknown_values() -> None:
    assert _map_item_type("Monografia") == "book"
    assert _map_item_type("Comentário bíblico") == "commentary"
    assert _map_item_type("Tipo Inventado") == "other"
