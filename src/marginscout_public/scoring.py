from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from types import MappingProxyType
from typing import Mapping


_HUNDRED = Decimal("100")
_WEIGHTS: Mapping[str, Decimal] = MappingProxyType(
    {
        # Illustrative public weights, not the complete private configuration.
        "request_intent": Decimal("0.30"),
        "service_fit": Decimal("0.20"),
        "specificity": Decimal("0.15"),
        "recency": Decimal("0.15"),
        "fulfillment_readiness": Decimal("0.10"),
        "budget_signal": Decimal("0.05"),
        "urgency": Decimal("0.05"),
    }
)


@dataclass(frozen=True)
class OpportunitySignals:
    request_intent: Decimal
    service_fit: Decimal
    specificity: Decimal
    recency: Decimal
    fulfillment_readiness: Decimal
    budget_signal: Decimal
    urgency: Decimal
    evidence_count: int
    material_risk_count: int = 0


@dataclass(frozen=True)
class ScoreFactor:
    name: str
    value: Decimal
    weight: Decimal
    contribution: Decimal


@dataclass(frozen=True)
class OpportunityScoreResult:
    score: Decimal
    confidence: Decimal
    label: str
    factors: tuple[ScoreFactor, ...]
    applied_caps: tuple[str, ...]


def score_opportunity(signals: OpportunitySignals) -> OpportunityScoreResult:
    """Calculate an explainable score; no model output or hidden state is used."""

    values = {
        "request_intent": signals.request_intent,
        "service_fit": signals.service_fit,
        "specificity": signals.specificity,
        "recency": signals.recency,
        "fulfillment_readiness": signals.fulfillment_readiness,
        "budget_signal": signals.budget_signal,
        "urgency": signals.urgency,
    }
    for name, value in values.items():
        if not Decimal("0") <= value <= _HUNDRED:
            raise ValueError(f"{name} must be between 0 and 100")
    if signals.evidence_count < 0 or signals.material_risk_count < 0:
        raise ValueError("counts cannot be negative")

    factors = tuple(
        ScoreFactor(
            name=name,
            value=value,
            weight=_WEIGHTS[name],
            contribution=(value * _WEIGHTS[name]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        )
        for name, value in values.items()
    )
    raw_score = sum((factor.contribution for factor in factors), Decimal("0"))
    caps: list[tuple[Decimal, str]] = []
    if signals.request_intent < Decimal("25"):
        caps.append((Decimal("35"), "service-request intent is not established"))
    if signals.fulfillment_readiness < Decimal("20"):
        caps.append((Decimal("65"), "fulfillment coverage is not ready"))
    if signals.material_risk_count >= 2:
        caps.append((Decimal("55"), "multiple material risks require review"))

    score = min([raw_score, *(cap for cap, _ in caps)]).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    confidence = min(
        _HUNDRED,
        Decimal(signals.evidence_count) * Decimal("20"),
    ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if score >= Decimal("75") and confidence >= Decimal("60"):
        label = "strong"
    elif score >= Decimal("45"):
        label = "review"
    else:
        label = "weak"

    return OpportunityScoreResult(
        score=score,
        confidence=confidence,
        label=label,
        factors=factors,
        applied_caps=tuple(reason for _, reason in caps),
    )
