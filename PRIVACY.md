# MarginScout Privacy and Deletion Policy

**Effective date:** September 21, 2026  
**Last updated:** September 21, 2026

## 1. Scope and current status

This policy describes how the MarginScout project handles information in its public engineering showcase and in the proposed Reddit API integration.

MarginScout is currently a private, single-operator decision-support application. **Live Reddit collection is not active or approved.** The implemented demonstration uses operator-supplied content and synthetic fixtures that do not represent real people and do not make Reddit network requests.

If Reddit grants written approval for live commercial API use, MarginScout will activate only the access and data practices permitted by that approval. This policy will be updated if the approved scope differs from the proposal below.

## 2. Information the proposed integration would process

For public posts returned by an approved, OAuth-authenticated Reddit API endpoint, MarginScout proposes to process only:

- Reddit post ID and permalink;
- subreddit name;
- post title and self-text;
- post creation time;
- author username when permitted and not deleted;
- post score and comment count;
- deletion or removal state; and
- operational metadata needed for compliance, such as retrieval time and Reddit rate-limit headers.

Public post text may contain information voluntarily included by its author. MarginScout will not separately enrich that text with off-platform identity information or attempt to identify the person behind a Reddit account.

MarginScout does not propose to collect private messages, chat content, private-subreddit content, individual voting histories, email addresses from Reddit account data, IP addresses, device identifiers, precise location, or inferred sensitive characteristics.

## 3. Purpose of processing

MarginScout would use approved public posts to:

- identify posts that may contain a request for professional services;
- remove duplicates and obviously irrelevant records;
- estimate whether a request matches a service the operator can responsibly fulfill;
- place plausible records into a private inbox for human review; and
- reconcile edits, removals, and deleted accounts.

MarginScout does not automatically contact a Reddit user, apply for work, post, comment, vote, send a direct message, purchase a service, or make a final business decision.

## 4. Automated processing and AI

The proposed baseline uses deterministic local rules for deduplication, filtering, service matching, recency, and review prioritization. Scores are decision-support signals only; a human controls all workflow and external actions.

Reddit content will not be sent to OpenAI or another third-party AI provider unless Reddit's written approval expressly permits that processing and this policy is updated to identify the processor, purpose, safeguards, and applicable retention. Reddit content will not be used to train an AI or machine-learning model.

## 5. Retention

Unless Reddit approves a different period in writing, raw Reddit content and author identifiers will use a maximum retention period of **48 hours from collection**. Content may be removed sooner when it is no longer required for the approved purpose.

Expiry and deletion must traverse every retained copy, including:

- source-ingestion records;
- lead-review records and observations;
- assessment evidence and result snapshots;
- model or agent payloads, if such processing is ever separately approved;
- caches and exports; and
- any downstream local record containing copied Reddit content.

MarginScout will not keep deleted Reddit content in de-identified, anonymized, or tombstoned form. A non-content compliance event may be retained only when Reddit's written agreement permits it.

## 6. Reddit edits, removals, and account deletion

The proposed integration includes recurring reconciliation of retained records within the approved interval.

- When a post is deleted or removed, MarginScout will remove its title, body, embedded links, author reference, and other copied content.
- When an account is deleted, MarginScout will remove author-identifying information associated with that account.
- If reconciliation is overdue or unhealthy, live collection will stop until the issue is resolved.

## 7. Sharing and sale

MarginScout will not sell, license, redistribute, or expose Reddit data as a product, dataset, advertising audience, or third-party feed. It will not use Reddit data for targeted advertising, user profiling, surveillance, or re-identification.

Information may be disclosed when required by applicable law or a valid legal process. No other sharing is proposed unless Reddit's written approval permits it and this policy is updated first.

## 8. Security

MarginScout is designed to:

- keep OAuth credentials and API keys in runtime secrets rather than source code or database settings;
- restrict access to the private operator environment;
- use exact approved hosts, communities, endpoints, and request limits;
- omit credentials and source bodies from application logs;
- treat all source content as untrusted data rather than executable instructions; and
- fail closed when approval, credentials, retention, rate-limit, or deletion-health checks are not satisfied.

No system can guarantee absolute security. A suspected issue involving this public source excerpt can be reported using the contact in `SECURITY.md`.

## 9. Access and deletion requests

To ask whether MarginScout holds content associated with a Reddit post or username, or to request deletion, contact:

**Email:** `<PRIVACY_CONTACT_EMAIL>`

Include only the Reddit post URL, post ID, or username needed to locate the record. Do not send passwords, OAuth tokens, government identification, or other unnecessary sensitive information. A request may need to be verified to prevent unauthorized deletion or disclosure.

MarginScout will also honor removals communicated through Reddit's approved compliance process when applicable.

## 10. Changes to this policy

Material changes will be published in this file with an updated date. Live Reddit access will not be activated until the policy, implementation, and written approval agree on the permitted purpose, data fields, retention, deletion, attribution, security, and third-party processing.

## 11. Contact

MarginScout project operator  
**Privacy contact:** `<PRIVACY_CONTACT_EMAIL>`

