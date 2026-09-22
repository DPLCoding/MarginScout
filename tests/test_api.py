from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from marginscout_public.api import create_app  # noqa: E402


class PublicApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_capabilities_are_truthful_about_external_access(self) -> None:
        response = self.client.get("/api/v1/capabilities")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["personal_single_user"])
        self.assertTrue(response.json()["deterministic_assessment"])
        self.assertFalse(response.json()["live_reddit"])
        self.assertFalse(response.json()["automated_outreach"])
        self.assertFalse(response.json()["automated_reddit_interaction"])
        self.assertFalse(response.json()["reddit_content_model_training"])

    def test_assessment_returns_factors_and_human_authority(self) -> None:
        response = self.client.post(
            "/api/v1/opportunities/assess",
            json={
                "request_intent": 95,
                "service_fit": 90,
                "specificity": 80,
                "recency": 90,
                "fulfillment_readiness": 85,
                "budget_signal": 70,
                "urgency": 60,
                "evidence_count": 5,
                "material_risk_count": 0,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["score"], "87.0")
        self.assertEqual(payload["label"], "strong")
        self.assertEqual(payload["decision_authority"], "human")
        self.assertEqual(len(payload["factors"]), 7)

    def test_assessment_rejects_invalid_signal(self) -> None:
        response = self.client.post(
            "/api/v1/opportunities/assess",
            json={
                "request_intent": 101,
                "service_fit": 0,
                "specificity": 0,
                "recency": 0,
                "fulfillment_readiness": 0,
                "budget_signal": 0,
                "urgency": 0,
                "evidence_count": 0,
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
