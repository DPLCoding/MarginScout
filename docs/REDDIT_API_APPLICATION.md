# Reddit API access application draft

Replace every angle-bracket placeholder and verify the final text against Reddit's current form and policies before submitting. Be direct that this is a commercial lead-research use case; do not describe it as personal or non-commercial.

## Contact and source code

- Applicant: `David Plam`
- Email: `dyuchuan@gmail.com`
- Reddit account: `/u/PloomponPloom`
- Application name: `MarginScout`
- Public source-review repository: `https://github.com/DPLCoding/MarginScout`
- Privacy and deletion policy: `https://github.com/DPLCoding/MarginScout/blob/main/PRIVACY.md`

The linked repository is explicitly a sanitized architecture and integration excerpt, not the complete private production repository. It contains the proposed approval-gated client boundary, synthetic tests, data-handling documentation, and no secrets or live Reddit transport.

## Project summary

MarginScout is a single-operator, commercial decision-support application that helps me evaluate potential service-work opportunities and whether I have an appropriate fulfillment option. I am requesting read-only API access to monitor a small, fixed allowlist of public subreddits for newest posts that may contain requests for professional services. A human will review every candidate before taking any action outside Reddit. MarginScout will not automatically contact users, post, comment, vote, send messages, or perform moderation actions.

I understand this use may support revenue-generating work and am therefore requesting explicit written approval for commercial use. I will not sell, license, redistribute, or expose Reddit data as a product or feed.

## Exact requested access

I am requesting OAuth-authenticated read access to:

- `GET /r/{subreddit}/new` for `r/forhire`, `r/smallbusiness`, and `r/entrepreneur`, or a smaller subset Reddit approves;
- up to 25 posts per request;
- no more than one request per approved subreddit every 15 minutes, initially no more than 12 listing requests per hour total; and
- a bounded read-only recheck of retained post IDs solely to reconcile edits, removals, and account deletions within the approved retention period.

There will be no scheduled keyword search. If targeted or historical search is considered later, I will request separate approval before implementing it.

## Data and processing

For each approved public post, MarginScout proposes to process the post ID, permalink, subreddit, title, self-text, creation time, author name when permitted, score, comment count, and deletion/removal state. It will not access private messages, chat, private communities, individual voting data, email addresses, IP addresses, or device data.

Processing is local and deterministic by default: stable-ID/content deduplication, keyword and intent filtering, service-category matching, recency scoring, and routing to a human review inbox. Reddit content will not be sent to OpenAI or another third-party model unless Reddit's written approval expressly allows that processing. It will not be used for model training or sensitive-trait inference.

## Retention, deletion, and security

Raw Reddit content and author identifiers will have a default maximum lifetime of 48 hours unless our written agreement specifies a different period. The application will recheck retained records, remove deleted post/comment content, remove identifying author data after account deletion, and stop collection if reconciliation is unhealthy. Redaction traverses source records, review records, evidence snapshots, caches, and any downstream local copy.

Credentials will be stored only in the runtime environment or a secret manager, never in source code or database settings. The client will use a truthful unique User-Agent in Reddit's required format, monitor `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset`, and obey the strictest of Reddit's headers, the written agreement, and a lower local ceiling.

Live Reddit records will link to the original post and identify Reddit as the source without implying endorsement. MarginScout will maintain a public privacy/deletion policy and an accessible deletion-request contact.

## Requested confirmation

Please confirm in writing:

1. whether this commercial lead-research purpose is approved;
2. the permitted OAuth client/application identity;
3. the approved communities, fields, endpoints, limits, and polling frequency;
4. the required retention and deletion-reconciliation interval;
5. the required attribution and app-label behavior;
6. whether any third-party AI classification is permitted (it will remain disabled unless explicitly approved);
7. any required privacy, security, audit, geographic, or user-deletion controls; and
8. any fees, agreement term, review date, or additional restrictions.

I will not activate live access until approval is granted and MarginScout has been configured to enforce the approved scope.

