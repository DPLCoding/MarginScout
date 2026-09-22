"""Public, non-operational MarginScout integration excerpt."""

from .reddit_client import (
    ApprovalScope,
    CollectionPage,
    HttpResponse,
    NormalizedPost,
    RedditReadOnlyClient,
)
from .scoring import OpportunityScoreResult, OpportunitySignals, score_opportunity

__all__ = [
    "ApprovalScope",
    "CollectionPage",
    "HttpResponse",
    "NormalizedPost",
    "RedditReadOnlyClient",
    "OpportunityScoreResult",
    "OpportunitySignals",
    "score_opportunity",
]
