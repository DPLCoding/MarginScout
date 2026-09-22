from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marginscout_public.scoring import LeadSignals, score_lead  # noqa: E402


class LeadScoringTests(unittest.TestCase):
    def test_strong_evidence_produces_explainable_score(self) -> None:
        result = score_lead(
            LeadSignals(
                buyer_intent=Decimal("95"),
                service_fit=Decimal("90"),
                specificity=Decimal("80"),
                recency=Decimal("90"),
                fulfillment_readiness=Decimal("85"),
                budget_signal=Decimal("70"),
                urgency=Decimal("60"),
                evidence_count=5,
            )
        )

        self.assertEqual(result.score, Decimal("87.0"))
        self.assertEqual(result.confidence, Decimal("100.0"))
        self.assertEqual(result.label, "strong")
        self.assertEqual(len(result.factors), 7)
        self.assertEqual(result.applied_caps, ())

    def test_keyword_match_without_buyer_intent_is_capped(self) -> None:
        result = score_lead(
            LeadSignals(
                buyer_intent=Decimal("10"),
                service_fit=Decimal("95"),
                specificity=Decimal("90"),
                recency=Decimal("100"),
                fulfillment_readiness=Decimal("90"),
                budget_signal=Decimal("80"),
                urgency=Decimal("70"),
                evidence_count=4,
            )
        )

        self.assertEqual(result.score, Decimal("35.0"))
        self.assertEqual(result.label, "weak")
        self.assertIn("buyer intent is not established", result.applied_caps)

    def test_out_of_range_signal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            score_lead(
                LeadSignals(
                    buyer_intent=Decimal("101"),
                    service_fit=Decimal("0"),
                    specificity=Decimal("0"),
                    recency=Decimal("0"),
                    fulfillment_readiness=Decimal("0"),
                    budget_signal=Decimal("0"),
                    urgency=Decimal("0"),
                    evidence_count=0,
                )
            )


if __name__ == "__main__":
    unittest.main()

