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
    assert key.startswith("hash:")
    assert len(key) == len("hash:") + 16
    # Deve ser determinístico: mesma entrada → mesmo resultado (index ignorado)
    assert _extract_source_key(record, source_id=7, index=3) == key
    assert _extract_source_key(record, source_id=7, index=99) == key


def test_deterministic_fallback_same_content_same_key() -> None:
    """Mesmo conteúdo em índices diferentes → mesmo hash (identidade por conteúdo)."""
    record = {"title": "Sem ID"}
    key_0 = _extract_source_key(record, source_id=1, index=0)
    key_1 = _extract_source_key(record, source_id=1, index=1)
    # Com o novo fallback por hash, o índice não afeta o resultado
    assert key_0 == key_1
    assert key_0.startswith("hash:")


def test_strips_whitespace_from_source_key() -> None:
    record = {"source_key": "  BK-001  "}
    assert _extract_source_key(record, source_id=1, index=0) == "BK-001"


def test_empty_source_key_falls_through_to_id() -> None:
    record = {"source_key": "   ", "id": "77"}
    assert _extract_source_key(record, source_id=1, index=0) == "77"


def test_none_source_key_falls_through_to_id() -> None:
    record = {"source_key": None, "id": "55"}
    assert _extract_source_key(record, source_id=1, index=0) == "55"


# --- Testes adicionais exigidos pela tarefa 3.2 ---

def test_source_key_fallback_is_deterministic() -> None:
    """Mesmo registro em ordens diferentes de chamada → mesmo hash."""
    record = {"title": "Registro Sem ID", "author": "Autor X"}
    key_a = _extract_source_key(record, source_id=1, index=0)
    key_b = _extract_source_key(record, source_id=1, index=99)
    assert key_a == key_b
    assert key_a.startswith("hash:")


def test_source_key_fallback_prefix() -> None:
    """Fallback deve ter prefixo 'hash:' seguido de exatamente 16 caracteres hex."""
    record = {"title": "Sem source_key e sem id"}
    key = _extract_source_key(record, source_id=5, index=0)
    assert key.startswith("hash:")
    suffix = key[len("hash:"):]
    assert len(suffix) == 16
    assert all(c in "0123456789abcdef" for c in suffix)


def test_source_key_uses_explicit_field_when_present() -> None:
    """Campo source_key ou id tem prioridade; ausência de ambos usa hash."""
    # source_key tem prioridade máxima
    record_with_source_key = {"source_key": "SK-42", "id": "99", "title": "T"}
    assert _extract_source_key(record_with_source_key, source_id=1, index=0) == "SK-42"

    # id é usado quando source_key está ausente
    record_with_id = {"id": "77", "title": "T"}
    assert _extract_source_key(record_with_id, source_id=1, index=0) == "77"

    # sem nenhum dos dois → fallback hash
    record_no_key = {"title": "Sem identificador"}
    key = _extract_source_key(record_no_key, source_id=1, index=0)
    assert key.startswith("hash:")
