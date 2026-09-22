from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import OpportunitySignals, score_opportunity


Percent = Annotated[Decimal, Field(ge=0, le=100)]


class OpportunityAssessmentRequest(BaseModel):
    request_intent: Percent
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
            "This is not the complete private MarginScout API."
        ),
    )

    @app.get("/health/ready")
    def health_ready() -> dict[str, object]:
        return {"status": "ready", "external_network_required": False}

    @app.get("/api/v1/capabilities")
    def capabilities() -> dict[str, object]:
        return {
            "personal_single_user": True,
            "deterministic_assessment": True,
            "synthetic_tests": True,
            "live_reddit": False,
            "automated_outreach": False,
            "automated_reddit_interaction": False,
            "reddit_content_model_training": False,
            "complete_application_included": False,
        }

    @app.post("/api/v1/opportunities/assess")
    def assess_opportunity(payload: OpportunityAssessmentRequest) -> dict[str, object]:
        result = score_opportunity(OpportunitySignals(**payload.model_dump()))
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
