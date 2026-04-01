"""Testes unitários: MatchScore e ConfidenceBand value objects."""

from __future__ import annotations

import pytest

from catalogo_acervo.domain.value_objects.match_score import ConfidenceBand, MatchScore

# --- ConfidenceBand.from_score ---


@pytest.mark.parametrize(
    ("score", "expected_band"),
    [
        (100.0, ConfidenceBand.HIGH),
        (90.0, ConfidenceBand.HIGH),
        (89.9, ConfidenceBand.MEDIUM),
        (70.0, ConfidenceBand.MEDIUM),
        (69.9, ConfidenceBand.LOW),
        (50.0, ConfidenceBand.LOW),
        (49.9, ConfidenceBand.REJECTED),
        (0.0, ConfidenceBand.REJECTED),
    ],
)
def test_confidence_band_thresholds(score: float, expected_band: ConfidenceBand) -> None:
    assert ConfidenceBand.from_score(score) == expected_band


# --- MatchScore.create ---


def test_match_score_create_derives_band() -> None:
    ms = MatchScore.create(score=85.0, rule="title+author_fuzzy")
    assert ms.score == 85.0
    assert ms.band == ConfidenceBand.MEDIUM
    assert ms.rule == "title+author_fuzzy"


def test_match_score_score_is_rounded() -> None:
    ms = MatchScore.create(score=85.1234, rule="r")
    assert ms.score == 85.12


def test_match_score_rejects_out_of_range_low() -> None:
    with pytest.raises(ValueError, match="score deve estar em"):
        MatchScore.create(score=-1.0, rule="r")


def test_match_score_rejects_out_of_range_high() -> None:
    with pytest.raises(ValueError, match="score deve estar em"):
        MatchScore.create(score=100.01, rule="r")


def test_match_score_is_frozen() -> None:
    ms = MatchScore.create(score=75.0, rule="r")
    with pytest.raises(Exception):  # noqa: B017
        ms.score = 99.0  # type: ignore[misc]


# --- is_actionable ---


def test_is_actionable_true_for_high() -> None:
    ms = MatchScore.create(score=95.0, rule="r")
    assert ms.is_actionable() is True


def test_is_actionable_true_for_medium() -> None:
    ms = MatchScore.create(score=75.0, rule="r")
    assert ms.is_actionable() is True


def test_is_actionable_false_for_low() -> None:
    ms = MatchScore.create(score=55.0, rule="r")
    assert ms.is_actionable() is False


def test_is_actionable_false_for_rejected() -> None:
    ms = MatchScore.create(score=30.0, rule="r")
    assert ms.is_actionable() is False


# --- suggest_match integration ---


def test_suggest_match_returns_match_score() -> None:
    from catalogo_acervo.domain.entities.catalog_item import CatalogItem
    from catalogo_acervo.domain.services.matching import suggest_match

    a = CatalogItem(
        source_id=1,
        source_key="a",
        title_raw="Teologia Sistemática",
        title_norm="teologia sistematica",
        author_norm="wayne grudem",
    )
    b = CatalogItem(
        source_id=2,
        source_key="b",
        title_raw="Teologia Sistemática",
        title_norm="teologia sistematica",
        author_norm="wayne grudem",
    )
    result = suggest_match(a, b)
    assert isinstance(result, MatchScore)
    assert result.score == 100.0
    assert result.band == ConfidenceBand.HIGH
    assert result.is_actionable() is True
