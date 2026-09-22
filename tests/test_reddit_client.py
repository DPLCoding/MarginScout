from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marginscout_public.reddit_client import (  # noqa: E402
    ApprovalRequiredError,
    ApprovalScope,
    HttpResponse,
    RedditRateLimitError,
    RedditReadOnlyClient,
)
from marginscout_public.retention import decide_redaction  # noqa: E402


NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


class FakeTokenProvider:
    def __init__(self) -> None:
        self.calls = 0

    def access_token(self) -> str:
        self.calls += 1
        return "synthetic-test-token"


class FakeTransport:
    def __init__(self, response: HttpResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get(self, url: str, *, headers, timeout_seconds: float) -> HttpResponse:
        self.calls.append((url, dict(headers), timeout_seconds))
        return self.response


def approval(*, intended_use: bool = True) -> ApprovalScope:
    return ApprovalScope(
        approval_reference="synthetic-approval-reference",
        approved_by="synthetic-reviewer",
        effective_at=NOW - timedelta(days=1),
        expires_at=NOW + timedelta(days=30),
        permitted_communities=frozenset({"forhire"}),
        intended_use_approved=intended_use,
        max_requests_per_hour=12,
        max_items_per_request=25,
        retention_hours=48,
    )


def listing_response(*, status_code: int = 200, deleted: bool = False) -> HttpResponse:
    post = {
        "id": "abc123",
        "subreddit": "forhire",
        "permalink": "/r/forhire/comments/abc123/need_a_site/",
        "created_utc": 1_768_478_400,
        "title": "[Hiring] Small business website",
        "selftext": "Seeking a developer for a five-page informational site.",
        "author": "synthetic_requester",
        "score": 3,
        "num_comments": 2,
    }
    if deleted:
        post.update({"title": "[deleted]", "selftext": "[deleted]", "author": "[deleted]"})
    return HttpResponse(
        status_code=status_code,
        headers={
            "X-Ratelimit-Used": "1",
            "X-Ratelimit-Remaining": "99",
            "X-Ratelimit-Reset": "600",
        },
        body={"data": {"after": "t3_next1", "children": [{"kind": "t3", "data": post}]}},
    )


class RedditClientTests(unittest.TestCase):
    def make_client(self, scope: ApprovalScope, response: HttpResponse):
        tokens = FakeTokenProvider()
        transport = FakeTransport(response)
        client = RedditReadOnlyClient(
            approval=scope,
            user_agent="windows:marginscout:v0.1 (by /u/example_developer)",
            token_provider=tokens,
            transport=transport,
            clock=lambda: NOW,
        )
        return client, tokens, transport

    def test_missing_intended_use_approval_fails_before_credentials_or_transport(self) -> None:
        client, tokens, transport = self.make_client(
            approval(intended_use=False), listing_response()
        )

        with self.assertRaises(ApprovalRequiredError):
            client.collect_new("forhire")

        self.assertEqual(tokens.calls, 0)
        self.assertEqual(transport.calls, [])

    def test_unapproved_community_fails_closed(self) -> None:
        client, tokens, transport = self.make_client(approval(), listing_response())

        with self.assertRaises(ApprovalRequiredError):
            client.collect_new("jobs")

        self.assertEqual(tokens.calls, 0)
        self.assertEqual(transport.calls, [])

    def test_collects_only_bounded_new_listing_and_reports_rate_state(self) -> None:
        client, tokens, transport = self.make_client(approval(), listing_response())

        page = client.collect_new("r/forhire", limit=10)

        self.assertEqual(tokens.calls, 1)
        self.assertEqual(len(transport.calls), 1)
        url, headers, timeout = transport.calls[0]
        self.assertEqual(
            url,
            "https://oauth.reddit.com/r/forhire/new?limit=10&raw_json=1",
        )
        self.assertEqual(headers["User-Agent"], "windows:marginscout:v0.1 (by /u/example_developer)")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertEqual(timeout, 10.0)
        self.assertEqual(page.after, "t3_next1")
        self.assertEqual(page.rate_limit.remaining, 99.0)
        self.assertEqual(len(page.items), 1)
        self.assertEqual(page.items[0].external_id, "abc123")
        self.assertEqual(page.items[0].community, "forhire")
        self.assertEqual(
            page.items[0].source_url,
            "https://www.reddit.com/r/forhire/comments/abc123/need_a_site/",
        )

    def test_deleted_content_is_not_returned(self) -> None:
        client, _, _ = self.make_client(approval(), listing_response(deleted=True))

        post = client.collect_new("forhire").items[0]

        self.assertTrue(post.deleted_or_removed)
        self.assertEqual(post.title, "")
        self.assertEqual(post.body, "")
        self.assertIsNone(post.author)

    def test_rate_limit_response_is_explicit(self) -> None:
        client, _, _ = self.make_client(approval(), listing_response(status_code=429))

        with self.assertRaises(RedditRateLimitError) as raised:
            client.collect_new("forhire")

        self.assertEqual(raised.exception.reset_seconds, 600.0)

    def test_result_limit_cannot_exceed_written_scope(self) -> None:
        client, tokens, transport = self.make_client(approval(), listing_response())

        with self.assertRaises(ValueError):
            client.collect_new("forhire", limit=26)

        self.assertEqual(tokens.calls, 0)
        self.assertEqual(transport.calls, [])


class RetentionTests(unittest.TestCase):
    def test_expired_source_content_and_author_are_redacted(self) -> None:
        decision = decide_redaction(
            collected_at=NOW - timedelta(hours=49),
            now=NOW,
            retention_hours=48,
        )
        self.assertTrue(decision.redact_content)
        self.assertTrue(decision.redact_author)
        self.assertEqual(decision.reason, "retention_expired")

    def test_deleted_account_redacts_author_before_content_expiry(self) -> None:
        decision = decide_redaction(
            collected_at=NOW - timedelta(hours=1),
            now=NOW,
            retention_hours=48,
            author_account_deleted=True,
        )
        self.assertFalse(decision.redact_content)
        self.assertTrue(decision.redact_author)
        self.assertEqual(decision.reason, "author_account_deleted")


if __name__ == "__main__":
    unittest.main()
