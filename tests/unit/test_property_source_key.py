"""Property-based tests for source_key fallback determinism.

# Feature: core-integrity-fixes, Property 6: source_key fallback determinism
"""

from __future__ import annotations

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from catalogo_acervo.application.use_cases.import_source_items_from_source import (
    _extract_source_key,
)

# ---------------------------------------------------------------------------
# Property 6: source_key fallback determinism
# Validates: Requirements 3.1, 3.2, 3.3
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(st.dictionaries(st.text(), st.text()))
def test_property_source_key_fallback_determinism(record: dict[str, str]) -> None:
    """For any record without 'source_key' or 'id', calling _extract_source_key
    with different index values must return the same result (determinism).
    The result must also start with 'hash:' (correct format).

    Feature: core-integrity-fixes, Property 6: source_key fallback determinism
    Validates: Requirements 3.1, 3.2, 3.3
    """
    # Skip records that have explicit key fields — those bypass the fallback
    assume("source_key" not in record)
    assume("id" not in record)

    result_index_0 = _extract_source_key(record, source_id=1, index=0)
    result_index_99 = _extract_source_key(record, source_id=1, index=99)

    assert result_index_0 == result_index_99, (
        f"Fallback source_key is not deterministic: "
        f"index=0 → {result_index_0!r}, index=99 → {result_index_99!r}"
    )
    assert result_index_0.startswith("hash:"), (
        f"Fallback source_key must start with 'hash:', got {result_index_0!r}"
    )
