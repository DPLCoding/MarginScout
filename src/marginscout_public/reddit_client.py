from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import urlencode


OAUTH_ORIGIN = "https://oauth.reddit.com"
REDDIT_WEB_ORIGIN = "https://www.reddit.com"
_COMMUNITY_PATTERN = re.compile(r"[A-Za-z0-9_]{2,21}")
_AFTER_PATTERN = re.compile(r"t3_[a-z0-9]+")
_USER_AGENT_PATTERN = re.compile(r"^[^:]+:[^:]+:[^ ]+ \(by /u/[A-Za-z0-9_-]+\)$")


class RedditClientError(RuntimeError):
    """Base failure for the public client boundary."""


class ApprovalRequiredError(RedditClientError):
    """Raised before credentials or transport when written scope is not current."""


class RedditResponseError(RedditClientError):
    """Raised for malformed or unsuccessful API responses."""


class RedditRateLimitError(RedditResponseError):
    def __init__(self, reset_seconds: float | None) -> None:
        super().__init__("Reddit rate limit reached")
        self.reset_seconds = reset_seconds


class TokenProvider(Protocol):
    def access_token(self) -> str: ...


class HttpTransport(Protocol):
    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> "HttpResponse": ...


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: Mapping[str, str]
    body: Mapping[str, Any]


@dataclass(frozen=True)
class ApprovalScope:
    """Non-secret facts copied from the controlling written approval."""

    approval_reference: str
    approved_by: str
    effective_at: datetime
    expires_at: datetime
    permitted_communities: frozenset[str]
    commercial_use_approved: bool
    max_requests_per_hour: int
    max_items_per_request: int
    retention_hours: int
    third_party_ai_allowed: bool = False

    def assert_current(self, *, community: str, now: datetime) -> None:
        if not self.approval_reference.strip() or not self.approved_by.strip():
            raise ApprovalRequiredError("A written approval reference and approver are required")
        if not self.commercial_use_approved:
            raise ApprovalRequiredError("Written commercial-use approval is required")
        if now.tzinfo is None:
            raise ApprovalRequiredError("Approval checks require a timezone-aware timestamp")
        if not (self.effective_at <= now < self.expires_at):
            raise ApprovalRequiredError("The written approval is not currently effective")
        allowed = {normalize_community(item).casefold() for item in self.permitted_communities}
        if community.casefold() not in allowed:
            raise ApprovalRequiredError(f"r/{community} is outside the written approval scope")
        if self.max_requests_per_hour < 1 or self.max_items_per_request < 1:
            raise ApprovalRequiredError("The written approval must include positive request limits")
        if self.retention_hours < 1:
            raise ApprovalRequiredError("The written approval must include a retention limit")


@dataclass(frozen=True)
class RateLimitState:
    used: float | None
    remaining: float | None
    reset_seconds: float | None


@dataclass(frozen=True)
class NormalizedPost:
    external_id: str
    community: str
    source_url: str
    title: str
    body: str
    author: str | None
    posted_at: datetime
    score: int
    comment_count: int
    deleted_or_removed: bool


@dataclass(frozen=True)
class CollectionPage:
    items: tuple[NormalizedPost, ...]
    after: str | None
    rate_limit: RateLimitState


def normalize_community(value: str) -> str:
    community = value.strip()
    if community.lower().startswith("r/"):
        community = community[2:]
    if not _COMMUNITY_PATTERN.fullmatch(community):
        raise ValueError("Community must be a valid subreddit name")
    return community


class RedditReadOnlyClient:
    """Approval-gated `/new` client with injected credentials and transport.

    This public excerpt deliberately supplies no concrete token provider or HTTP
    transport. The tests use fakes and perform zero network requests.
    """

    def __init__(
        self,
        *,
        approval: ApprovalScope,
        user_agent: str,
        token_provider: TokenProvider,
        transport: HttpTransport,
        clock: Callable[[], datetime] | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not _USER_AGENT_PATTERN.fullmatch(user_agent):
            raise ValueError(
                "User-Agent must be truthful and formatted as "
                "<platform>:<app-id>:<version> (by /u/<username>)"
            )
        if not 0 < timeout_seconds <= 30:
            raise ValueError("timeout_seconds must be between 0 and 30")
        self._approval = approval
        self._user_agent = user_agent
        self._token_provider = token_provider
        self._transport = transport
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._timeout_seconds = timeout_seconds

    def collect_new(
        self,
        community: str,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> CollectionPage:
        normalized_community = normalize_community(community)
        now = self._clock()

        # The gate intentionally runs before a token is requested or transport is touched.
        self._approval.assert_current(community=normalized_community, now=now)
        if not 1 <= limit <= self._approval.max_items_per_request:
            raise ValueError(
                f"limit must be between 1 and {self._approval.max_items_per_request}"
            )
        if after is not None and not _AFTER_PATTERN.fullmatch(after):
            raise ValueError("after must be a Reddit t3 fullname")

        query: dict[str, str | int] = {"limit": limit, "raw_json": 1}
        if after:
            query["after"] = after
        url = f"{OAUTH_ORIGIN}/r/{normalized_community}/new?{urlencode(query)}"
        token = self._token_provider.access_token().strip()
        if not token:
            raise RedditClientError("Token provider returned an empty OAuth token")

        response = self._transport.get(
            url,
            headers=MappingProxyType(
                {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": self._user_agent,
                    "Accept": "application/json",
                }
            ),
            timeout_seconds=self._timeout_seconds,
        )
        rate_limit = _rate_limit_state(response.headers)
        if response.status_code == 429:
            raise RedditRateLimitError(rate_limit.reset_seconds)
        if response.status_code in {401, 403}:
            raise RedditResponseError("Reddit rejected the OAuth identity or approved scope")
        if not 200 <= response.status_code < 300:
            raise RedditResponseError(f"Unexpected Reddit response status {response.status_code}")

        return _normalize_listing(
            response.body,
            expected_community=normalized_community,
            rate_limit=rate_limit,
        )


def _normalize_listing(
    payload: Mapping[str, Any],
    *,
    expected_community: str,
    rate_limit: RateLimitState,
) -> CollectionPage:
    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise RedditResponseError("Listing response is missing its data object")
    children = data.get("children")
    if not isinstance(children, list):
        raise RedditResponseError("Listing response is missing its children list")

    items: list[NormalizedPost] = []
    for child in children:
        if not isinstance(child, Mapping) or child.get("kind") != "t3":
            continue
        raw = child.get("data")
        if not isinstance(raw, Mapping):
            continue
        post = _normalize_post(raw, expected_community=expected_community)
        if post is not None:
            items.append(post)

    after = data.get("after")
    if after is not None and (not isinstance(after, str) or not _AFTER_PATTERN.fullmatch(after)):
        raise RedditResponseError("Listing response contains an invalid pagination cursor")
    return CollectionPage(items=tuple(items), after=after, rate_limit=rate_limit)


def _normalize_post(
    raw: Mapping[str, Any],
    *,
    expected_community: str,
) -> NormalizedPost | None:
    external_id = _bounded_text(raw.get("id"), 32)
    community = _bounded_text(raw.get("subreddit"), 64)
    permalink = _bounded_text(raw.get("permalink"), 500)
    created = raw.get("created_utc")
    if not external_id or not community or community.casefold() != expected_community.casefold():
        return None
    if not permalink.startswith(f"/r/{community}/comments/"):
        return None
    if not isinstance(created, (int, float)):
        return None

    title = _bounded_text(raw.get("title"), 500)
    body = _bounded_text(raw.get("selftext"), 20_000)
    author = _bounded_text(raw.get("author"), 64) or None
    removed_marker = _bounded_text(raw.get("removed_by_category"), 80)
    deleted_or_removed = bool(removed_marker) or title.casefold() in {"[deleted]", "[removed]"}
    deleted_or_removed = deleted_or_removed or body.casefold() in {"[deleted]", "[removed]"}
    deleted_or_removed = deleted_or_removed or (author or "").casefold() == "[deleted]"
    if deleted_or_removed:
        title = ""
        body = ""
        author = None

    return NormalizedPost(
        external_id=external_id,
        community=community,
        source_url=f"{REDDIT_WEB_ORIGIN}{permalink}",
        title=title,
        body=body,
        author=author,
        posted_at=datetime.fromtimestamp(float(created), tz=timezone.utc),
        score=_integer(raw.get("score")),
        comment_count=_integer(raw.get("num_comments")),
        deleted_or_removed=deleted_or_removed,
    )


def _rate_limit_state(headers: Mapping[str, str]) -> RateLimitState:
    lowered = {str(key).casefold(): str(value) for key, value in headers.items()}
    return RateLimitState(
        used=_optional_float(lowered.get("x-ratelimit-used")),
        remaining=_optional_float(lowered.get("x-ratelimit-remaining")),
        reset_seconds=_optional_float(lowered.get("x-ratelimit-reset")),
    )


def _bounded_text(value: Any, maximum: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:maximum]


def _integer(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

