from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from typing import Mapping


class ModelTier(StrEnum):
    FAST = "fast"
    REASONING = "reasoning"
    PREMIUM = "premium"


class ModelTask(StrEnum):
    QUERY_GENERATION = "query_generation"
    BULK_EXTRACTION = "bulk_extraction"
    CANDIDATE_COMPARISON = "candidate_comparison"
    DEEP_REVIEW = "deep_review"


@dataclass(frozen=True)
class ModelPrice:
    model_name: str
    input_usd_per_million: Decimal
    output_usd_per_million: Decimal
    request_fee_usd: Decimal = Decimal("0")
    enabled: bool = True


@dataclass(frozen=True)
class UsageEstimate:
    requests: int
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class RoutingDecision:
    task: ModelTask
    tier: ModelTier
    model_name: str
    estimated_cost_usd: Decimal
    premium_fallback_used: bool


class ModelRouter:
    """Configuration-driven routing; model names and prices are runtime inputs."""

    _DEFAULTS = {
        ModelTask.QUERY_GENERATION: ModelTier.FAST,
        ModelTask.BULK_EXTRACTION: ModelTier.FAST,
        ModelTask.CANDIDATE_COMPARISON: ModelTier.REASONING,
        ModelTask.DEEP_REVIEW: ModelTier.PREMIUM,
    }

    def __init__(
        self,
        prices: Mapping[ModelTier, ModelPrice],
        *,
        premium_enabled: bool = False,
    ) -> None:
        self._prices = dict(prices)
        self._premium_enabled = premium_enabled

    def route(self, task: ModelTask, usage: UsageEstimate) -> RoutingDecision:
        if usage.requests < 0 or usage.input_tokens < 0 or usage.output_tokens < 0:
            raise ValueError("usage estimates cannot be negative")
        requested = self._DEFAULTS[task]
        fallback_used = requested is ModelTier.PREMIUM and not self._premium_enabled
        tier = ModelTier.REASONING if fallback_used else requested
        price = self._prices.get(tier)
        if price is None or not price.enabled or not price.model_name.strip():
            raise ValueError(f"No enabled model is configured for the {tier.value} tier")

        million = Decimal("1000000")
        cost = (
            Decimal(usage.requests) * price.request_fee_usd
            + Decimal(usage.input_tokens) / million * price.input_usd_per_million
            + Decimal(usage.output_tokens) / million * price.output_usd_per_million
        ).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        return RoutingDecision(
            task=task,
            tier=tier,
            model_name=price.model_name,
            estimated_cost_usd=cost,
            premium_fallback_used=fallback_used,
        )

