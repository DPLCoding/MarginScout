# Reddit API access application draft

Verify this statement against Reddit's current form and policies before submitting. It describes MarginScout's current purpose as a personal, single-user developer application and does not claim that API access has already been approved.

## Contact and source code

- Applicant: `David Plam`
- Email: `dyuchuan@gmail.com`
- Reddit account: `/u/PloomponPloom`
- Application name: `MarginScout`
- Public source-review repository: `https://github.com/DPLCoding/MarginScout`
- Privacy and deletion policy: `https://github.com/DPLCoding/MarginScout/blob/main/PRIVACY.md`

The linked repository is explicitly a sanitized architecture and integration excerpt, not the complete private development repository. It contains the proposed approval-gated client boundary, synthetic tests, data-handling documentation, and no secrets or concrete live Reddit transport.

## Project summary

MarginScout is a personal software engineering and portfolio project operated privately by me as its only user. It is an external application with its own private dashboard that helps me organize and evaluate publicly available posts in which Reddit users explicitly discuss or request freelance, creative, technical, or business services. I am requesting read-only API access to retrieve recent public posts from a small, fixed allowlist of subreddits for relevance filtering, classification, and private review.

MarginScout is not sold, hosted for other users, or offered as a service. I will not sell, license, monetize, redistribute, or expose Reddit data or API access as a product or feed. The application will not automatically contact Reddit users, post, comment, vote, follow accounts, send messages, or perform moderation actions. If I choose to respond to a relevant post, I will manually open the original Reddit post and interact through Reddit as a normal user.

## Exact requested access

I am requesting OAuth-authenticated read access to:

- `GET /r/{subreddit}/new` for `r/forhire`, `r/smallbusiness`, and `r/entrepreneur`, or a smaller subset Reddit approves;
- up to 25 posts per request;
- no more than one request per approved subreddit every 15 minutes, initially no more than 12 listing requests per hour total; and
- a bounded read-only recheck of retained post IDs solely to reconcile edits, removals, and account deletions within the approved retention period.

There will be no scheduled keyword search. If targeted or historical search is considered later, I will request separate approval before implementing it.

## Data and processing

For each approved public post, MarginScout proposes to process the post ID, permalink, subreddit, title, self-text, creation time, author name when permitted, score, comment count, and deletion/removal state. It will not access private messages, chat, private communities, individual voting data, email addresses, IP addresses, or device data.

Processing is local and deterministic by default: stable-ID/content deduplication, request-language filtering, service-category matching, recency scoring, and routing to my private review inbox. Optional AI use is limited to inference/classification with structured output. Reddit content will not be sent to OpenAI or another external model provider unless Reddit's written approval expressly permits that processing. It will not be used to train or fine-tune a model, build a dataset, profile users, or infer sensitive traits.

## Retention, deletion, and security

Raw Reddit content and author identifiers will have a default maximum lifetime of 48 hours unless our written agreement specifies a different period. The application will recheck retained records, remove deleted post/comment content, remove identifying author data after account deletion, and stop collection if reconciliation is unhealthy. Redaction traverses source records, review records, evidence snapshots, caches, and any downstream local copy.

Credentials will be stored only in the runtime environment or a secret manager, never in source code or database settings. The client will use a truthful unique User-Agent in Reddit's required format, monitor `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset`, and obey the strictest of Reddit's headers, the written agreement, and a lower local ceiling.

Live Reddit records will link to the original post and identify Reddit as the source without implying endorsement. MarginScout will maintain a public privacy/deletion policy and an accessible deletion-request contact.

## Requested confirmation

Please confirm in writing:

1. whether the personal, single-user, read-only purpose described above is approved;
2. the permitted OAuth client/application identity;
3. the approved communities, fields, endpoints, limits, and polling frequency;
4. the required retention and deletion-reconciliation interval;
5. the required attribution and app-label behavior;
6. whether external AI inference/classification is permitted (it will remain disabled for Reddit content unless explicitly approved);
7. any required privacy, security, audit, geographic, or user-deletion controls; and
8. any fees, agreement term, review date, or additional restrictions.

I will not activate live access until approval is granted and MarginScout has been configured to enforce the approved scope.
