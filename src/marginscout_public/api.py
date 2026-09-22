from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import LeadSignals, score_lead


Percent = Annotated[Decimal, Field(ge=0, le=100)]


class LeadAssessmentRequest(BaseModel):
    buyer_intent: Percent
    service_fit: Percent
    specificity: Percent
    recency: Percent
    fulfillment_readiness: Percent
    budget_signal: Percent
    urgency: Percent
    evidence_count: int = Field(ge=0, le=20)
    material_risk_count: int = Field(default=0, ge=0, le=20)


def create_app() -> FastAPI:
    app = FastAPI(
        title="MarginScout Public Engineering Excerpt",
        version="0.1.0",
        description=(
            "A zero-network demonstration of deterministic assessment and capability reporting. "
            "This is not the production MarginScout API."
        ),
    )

    @app.get("/health/ready")
    def health_ready() -> dict[str, object]:
        return {"status": "ready", "external_network_required": False}

    @app.get("/api/v1/capabilities")
    def capabilities() -> dict[str, object]:
        return {
            "deterministic_assessment": True,
            "synthetic_tests": True,
            "live_reddit": False,
            "automated_outreach": False,
            "production_code_included": False,
        }

    @app.post("/api/v1/leads/assess")
    def assess_lead(payload: LeadAssessmentRequest) -> dict[str, object]:
        result = score_lead(LeadSignals(**payload.model_dump()))
        return {
            "score": str(result.score),
            "confidence": str(result.confidence),
            "label": result.label,
            "factors": [
                {
                    "name": factor.name,
                    "value": str(factor.value),
                    "weight": str(factor.weight),
                    "contribution": str(factor.contribution),
                }
                for factor in result.factors
            ],
            "applied_caps": list(result.applied_caps),
            "decision_authority": "human",
        }

    return app


app = create_app()

