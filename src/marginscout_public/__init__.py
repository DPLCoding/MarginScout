"""Public, non-production MarginScout integration excerpt."""

from .reddit_client import (
    ApprovalScope,
    CollectionPage,
    HttpResponse,
    NormalizedPost,
    RedditReadOnlyClient,
)
from .scoring import LeadScoreResult, LeadSignals, score_lead

__all__ = [
    "ApprovalScope",
    "CollectionPage",
    "HttpResponse",
    "NormalizedPost",
    "RedditReadOnlyClient",
    "LeadScoreResult",
    "LeadSignals",
    "score_lead",
]
