"""Value Object: MatchScore.

Encapsula o score de matching (0.0-100.0) e a classificação em banda
de confiança. Impede que código externo construa scores inválidos ou
que a banda seja ignorada.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, field_validator


class ConfidenceBand(str, Enum):
    """Classificação qualitativa do score de matching.

    Os limiares são conservadores por design: preferimos falsos negativos
    (deixar passar candidatos reais para revisão manual) a falsos positivos
    (fundir itens distintos automaticamente).

    high   ≥ 90  — merge automático seguro (requer política explícita)
    medium ≥ 70  — candidato forte para revisão humana
    low    ≥ 50  — candidato fraco, ruído provável
    rejected < 50 — descartado antes de persistir
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REJECTED = "rejected"

    @classmethod
    def from_score(cls, score: float) -> ConfidenceBand:
        if score >= 90.0:
            return cls.HIGH
        if score >= 70.0:
            return cls.MEDIUM
        if score >= 50.0:
            return cls.LOW
        return cls.REJECTED


class MatchScore(BaseModel):
    """Score de matching entre dois CatalogItems.

    score: float no intervalo [0.0, 100.0]
    rule:  identificador da regra que gerou o score (ex: 'title+author_fuzzy')
    band:  calculada automaticamente a partir do score
    """

    score: float
    rule: str
    band: ConfidenceBand = ConfidenceBand.REJECTED  # calculado no validator

    model_config = {"frozen": True}

    @field_validator("score")
    @classmethod
    def score_must_be_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError(f"score deve estar em [0.0, 100.0], recebido: {v}")
        return round(v, 2)

    @field_validator("band", mode="before")
    @classmethod
    def derive_band_from_score(cls, v: object, info: object) -> ConfidenceBand:
        # Se o chamador não passou band, deriva do score já validado.
        # Se passou explicitamente, respeita (permite override em testes).
        if isinstance(v, ConfidenceBand):
            return v
        # Acessa o score via info.data se disponível
        data = getattr(info, "data", {})
        score = data.get("score", 0.0)
        return ConfidenceBand.from_score(score)

    @classmethod
    def create(cls, score: float, rule: str) -> MatchScore:
        """Factory que deriva a banda automaticamente."""
        band = ConfidenceBand.from_score(score)
        return cls(score=score, rule=rule, band=band)

    def is_actionable(self) -> bool:
        """True se o score é alto o suficiente para revisão humana."""
        return self.band in (ConfidenceBand.HIGH, ConfidenceBand.MEDIUM)
