from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class RedactionDecision:
    redact_content: bool
    redact_author: bool
    reason: str | None
    deadline: datetime


def decide_redaction(
    *,
    collected_at: datetime,
    now: datetime,
    retention_hours: int,
    source_deleted_or_removed: bool = False,
    author_account_deleted: bool = False,
) -> RedactionDecision:
    """Return the deletion action; persistence traversal stays application-owned."""

    if collected_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("Retention timestamps must be timezone-aware")
    if retention_hours < 1:
        raise ValueError("retention_hours must be positive")

    deadline = collected_at + timedelta(hours=retention_hours)
    if source_deleted_or_removed:
        return RedactionDecision(True, True, "source_deleted_or_removed", deadline)
    if now >= deadline:
        return RedactionDecision(True, True, "retention_expired", deadline)
    if author_account_deleted:
        return RedactionDecision(False, True, "author_account_deleted", deadline)
    return RedactionDecision(False, False, None, deadline)

