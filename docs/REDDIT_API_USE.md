# Proposed Reddit API use

Status: **not approved and not active**. This document describes the access MarginScout is requesting; it does not claim authorization.

## Purpose

MarginScout is a personal software engineering project operated privately by one developer through its own dashboard. It would use approved public Reddit posts to organize posts in which users explicitly discuss or request freelance, creative, technical, or business services. The developer reviews every candidate. MarginScout is not sold or offered to other users; it does not contact Reddit users, automate replies, monetize API access, redistribute Reddit content, or provide a Reddit-data feed to anyone else.

## Requested read scope

- OAuth-authenticated, read-only access.
- `GET /r/{subreddit}/new` for a small allowlist approved by Reddit.
- Initial requested communities: `r/forhire`, `r/smallbusiness`, and `r/entrepreneur`, subject to Reddit's decision and each community's rules.
- At most 25 posts per listing request.
- At most one poll per approved community every 15 minutes (12 listing requests per hour for the initial three-community scope).
- A narrowly bounded post-state recheck solely to reconcile edits, deletions, and deleted accounts within the approved retention interval.
- No scheduled keyword search. Any future historical search capability would require separate approval and limits.

MarginScout will use the lower of its local request ceiling, Reddit's response-header limits, and any limit stated in the written agreement.

## Data fields

The proposed normalizer uses only fields needed for review and reconciliation:

- post ID and permalink;
- subreddit;
- title and self-text;
- post creation time;
- author name only when permitted and not deleted;
- score and comment count; and
- deletion/removal state and Reddit rate-limit headers.

The system does not collect private messages, chat, votes by individual users, email addresses, IP addresses, device data, browsing history, private subreddit content, or inferred sensitive characteristics.

## Processing

1. Enforce current written approval, exact community scope, credentials, request budget, and deletion-reconciliation health before any request.
2. Normalize bounded newest-post results and deduplicate by Reddit post ID and content hash.
3. Apply deterministic local filters for explicit service-request language, obvious offers/spam, already-filled requests, and irrelevant content.
4. Present plausible candidates to the developer for private human review.
5. Permit optional AI inference/classification only if the written approval expressly allows external model processing; otherwise keep Reddit processing deterministic-only.

Reddit content is not used to train or fine-tune a model. Source text is treated as untrusted data and cannot trigger tools or external actions.

## Retention and deletion

- Raw Reddit content and author identifiers use a maximum 48-hour default lifetime unless Reddit approves a different written retention period.
- Retained posts are rechecked for deletion/removal, and identifying author information is removed when an account is deleted.
- Source deletion traverses ingestion records, review records, observations, evidence snapshots, model payloads, caches, and any promoted local record containing source text.
- Deleted Reddit content is not retained in anonymized or tombstoned form. A non-content deletion audit is retained only if the written agreement expressly permits it.
- Expiry or failed reconciliation disables further collection.
- The developer can trigger source-record redaction and respond to a deletion request.

Final behavior will follow the written agreement if it is stricter than these proposed defaults.

## Attribution

Every displayed live record will identify Reddit as its source, link to the original post, show the applicable username only while permitted, and avoid implying Reddit endorsement. Exact presentation will follow Reddit's written requirements.

## Explicitly excluded behavior

- HTML scraping or unauthenticated JSON/RSS workarounds;
- votes, submissions, comments, moderation actions, chat, or direct messages;
- automated outreach, follows, or unsolicited communication;
- user profiling, re-identification, or sensitive-trait inference;
- data resale, monetization, redistribution, advertising targeting, or model training/fine-tuning; and
- attempts to evade access controls, rate limits, removals, or app labeling.
