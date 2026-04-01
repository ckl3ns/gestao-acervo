"""Testes unitários: extração e validação de source_key."""

from __future__ import annotations

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    _extract_source_key,
)


def test_prefer_source_key_field() -> None:
    record = {"source_key": "BK-001", "id": "99", "title": "Algum Título"}
    assert _extract_source_key(record, source_id=1, index=0) == "BK-001"


def test_fallback_to_id_when_no_source_key() -> None:
    record = {"id": "42", "title": "Algum Título"}
    assert _extract_source_key(record, source_id=1, index=0) == "42"


def test_fallback_deterministic_when_no_id_or_source_key() -> None:
    record = {"title": "Sem ID nenhum"}
    key = _extract_source_key(record, source_id=7, index=3)
    assert key == "auto:7:3"
    # Deve ser determinístico: mesma entrada → mesmo resultado
    assert _extract_source_key(record, source_id=7, index=3) == key


def test_deterministic_fallback_is_unique_per_index() -> None:
    record = {"title": "Sem ID"}
    key_0 = _extract_source_key(record, source_id=1, index=0)
    key_1 = _extract_source_key(record, source_id=1, index=1)
    assert key_0 != key_1


def test_strips_whitespace_from_source_key() -> None:
    record = {"source_key": "  BK-001  "}
    assert _extract_source_key(record, source_id=1, index=0) == "BK-001"


def test_empty_source_key_falls_through_to_id() -> None:
    record = {"source_key": "   ", "id": "77"}
    assert _extract_source_key(record, source_id=1, index=0) == "77"


def test_none_source_key_falls_through_to_id() -> None:
    record = {"source_key": None, "id": "55"}
    assert _extract_source_key(record, source_id=1, index=0) == "55"
