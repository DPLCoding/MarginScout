# Architecture overview

## Product boundary

MarginScout is a personal software engineering project operated privately by one developer. It separates source evidence, deterministic rules, optional model interpretation, and human workflow state so that an uncertain model response cannot silently become an asserted fact or external action. The application is not sold, hosted for other users, or offered as a service.

The complete product is private. This document intentionally describes components and controls without exposing proprietary prompts, scoring weights, provider records, or deployment details.

## Runtime topology

```mermaid
flowchart TB
    Browser[Next.js browser application]
    API[FastAPI REST service]
    Database[(PostgreSQL system of record)]
    Worker[Background worker]
    Scheduler[Opt-in polling scheduler]
    SourceGate[Approval and source-policy gate]
    External[Approved read-only external API]
    Models[Optional tool-free model providers]

    Browser -->|REST/JSON| API
    API --> Database
    Worker <-->|claim jobs and persist results| Database
    Scheduler -->|enqueue due jobs| Database
    Worker --> SourceGate
    SourceGate -->|bounded requests| External
    Worker -.->|bounded structured input| Models
```

- **Next.js** owns presentation and form state.
- **FastAPI** owns validation, canonicalization, state transitions, and API contracts.
- **PostgreSQL** is the system of record and durable job queue.
- **Workers** claim idempotent jobs atomically and persist progress, retries, costs, and outcomes.
- **Source adapters** are the only components permitted to perform approved external reads.
- **Model specialists** perform bounded inference/classification, have no tools, and cannot send messages, purchase services, or alter deterministic calculations. Source content is not training or fine-tuning data.

## Opportunity lifecycle

```mermaid
flowchart LR
    Capture[Manual or approved source capture]
    Normalize[Normalize and deduplicate]
    Filter[Local high-recall filter]
    Assess[Deterministic assessment]
    OptionalAI[Optional structured AI extraction]
    Review[Private candidate review]
    Qualify[Supply and economics qualification]
    Save[Manual save for follow-up]

    Capture --> Normalize --> Filter --> Assess
    Assess -. separately gated .-> OptionalAI
    Assess --> Review
    OptionalAI --> Review
    Review --> Qualify --> Save
```

A discovered record begins as source evidence and becomes a review candidate only when it merits the developer's attention. Saving it for further private evaluation always requires an explicit human action. Filtering, ranking, or model output cannot contact anyone or initiate a Reddit interaction.

## Reddit feed-first proposal

The proposed Reddit integration polls only bounded newest-post listings for an approved community allowlist. It does not schedule keyword-by-community search fan-out.

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant Q as Durable queue
    participant G as Approval gate
    participant R as Reddit OAuth API
    participant P as Candidate pipeline
    participant H as Developer

    S->>Q: Enqueue due source window
    Q->>G: Claim idempotent read job
    G->>G: Check written approval, expiry, scope, rate, retention health
    alt gate is current
        G->>R: GET approved /r/{community}/new
        R-->>G: Listing and rate-limit headers
        G->>P: Normalize bounded records
        P->>P: Deduplicate, filter, assess, route
        P-->>H: Review candidates
    else gate fails
        G-->>Q: Fail closed; no network request
    end
```

Live activation additionally requires environment-only OAuth credentials, truthful User-Agent identification, persistent rate accounting, source-edit and deletion reconciliation, approved attribution, and a public privacy/deletion path.

## Trust boundaries

### Source content

Marketplace and social content is untrusted data. It is character-bounded, normalized, and never interpreted as an instruction. Source text cannot choose tools, URLs, models, credentials, or workflow transitions.

### AI output

Optional model output is limited to inference/classification, must satisfy structured schemas, and must cite source evidence. It may suggest extracted requirements or ambiguities. It cannot override deterministic calculations, approval gates, hard risk controls, lifecycle status, or external permissions. Reddit content is not used to train or fine-tune a model.

### Secrets

Secrets remain in the runtime environment or a deployment secret manager. Database records may reference an environment-variable name but never contain the credential value. Logs omit request bodies, authorization headers, connection strings, and query strings.

### External actions

MarginScout exposes no automated apply, buy, post, comment, vote, follow, direct-message, email, moderation, or payment workflow. If the developer chooses to respond, they manually open the original Reddit post and interact through Reddit as a normal user.

## Reliability and observability

- Unique idempotency keys prevent duplicate execution for the same source window.
- Atomic database claims prevent two workers from processing one job.
- Retry counts and stale-claim recovery are bounded.
- Partial source failures remain visible rather than being flattened into success.
- Runs preserve source provenance, decision counts, warnings, latency, token usage, and estimated cost.
- Readiness distinguishes API-process health from database and durable-queue availability.
