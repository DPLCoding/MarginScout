from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marginscout_public.model_routing import (  # noqa: E402
    ModelPrice,
    ModelRouter,
    ModelTask,
    ModelTier,
    UsageEstimate,
)


PRICES = {
    ModelTier.FAST: ModelPrice("configured-fast-model", Decimal("0.20"), Decimal("1.20")),
    ModelTier.REASONING: ModelPrice(
        "configured-reasoning-model",
        Decimal("2.00"),
        Decimal("12.00"),
        request_fee_usd=Decimal("0.01"),
    ),
    ModelTier.PREMIUM: ModelPrice("configured-premium-model", Decimal("5.00"), Decimal("30.00")),
}


class ModelRoutingTests(unittest.TestCase):
    def test_bulk_extraction_uses_fast_tier(self) -> None:
        decision = ModelRouter(PRICES).route(
            ModelTask.BULK_EXTRACTION,
            UsageEstimate(requests=4, input_tokens=200_000, output_tokens=12_000),
        )
        self.assertEqual(decision.tier, ModelTier.FAST)
        self.assertEqual(decision.estimated_cost_usd, Decimal("0.054400"))

    def test_deep_review_falls_back_when_premium_is_disabled(self) -> None:
        decision = ModelRouter(PRICES, premium_enabled=False).route(
            ModelTask.DEEP_REVIEW,
            UsageEstimate(requests=1, input_tokens=1_000, output_tokens=100),
        )
        self.assertEqual(decision.tier, ModelTier.REASONING)
        self.assertTrue(decision.premium_fallback_used)
        self.assertEqual(decision.estimated_cost_usd, Decimal("0.013200"))

    def test_premium_requires_explicit_enablement(self) -> None:
        decision = ModelRouter(PRICES, premium_enabled=True).route(
            ModelTask.DEEP_REVIEW,
            UsageEstimate(requests=1, input_tokens=1_000, output_tokens=100),
        )
        self.assertEqual(decision.tier, ModelTier.PREMIUM)
        self.assertFalse(decision.premium_fallback_used)


if __name__ == "__main__":
    unittest.main()

