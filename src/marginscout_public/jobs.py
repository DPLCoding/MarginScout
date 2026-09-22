from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackgroundJob:
    id: UUID
    idempotency_key: str
    job_type: str
    payload: Mapping[str, Any]
    status: JobStatus
    attempts: int
    max_attempts: int
    available_at: datetime
    claimed_by: str | None = None
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    error_summary: str | None = None


class JobStore(Protocol):
    """Production implementations use an atomic persistent transaction."""

    def get(self, job_id: UUID) -> BackgroundJob | None: ...

    def get_by_idempotency_key(self, key: str) -> BackgroundJob | None: ...

    def insert(self, job: BackgroundJob) -> None: ...

    def replace(self, job: BackgroundJob) -> None: ...


class InMemoryJobStore:
    """Test/demo adapter; intentionally not represented as durable storage."""

    def __init__(self) -> None:
        self._items: dict[UUID, BackgroundJob] = {}
        self._keys: dict[str, UUID] = {}

    def get(self, job_id: UUID) -> BackgroundJob | None:
        return self._items.get(job_id)

    def get_by_idempotency_key(self, key: str) -> BackgroundJob | None:
        job_id = self._keys.get(key)
        return self._items.get(job_id) if job_id else None

    def insert(self, job: BackgroundJob) -> None:
        if job.idempotency_key in self._keys:
            raise JobStateError("idempotency key already exists")
        self._items[job.id] = job
        self._keys[job.idempotency_key] = job.id

    def replace(self, job: BackgroundJob) -> None:
        if job.id not in self._items:
            raise JobStateError("job does not exist")
        self._items[job.id] = job


class JobService:
    def __init__(self, store: JobStore) -> None:
        self._store = store

    def enqueue(
        self,
        *,
        idempotency_key: str,
        job_type: str,
        payload: Mapping[str, Any],
        max_attempts: int = 3,
        now: datetime | None = None,
    ) -> tuple[BackgroundJob, bool]:
        key = idempotency_key.strip()
        if not key or len(key) > 160:
            raise ValueError("idempotency_key must contain 1 to 160 characters")
        if not job_type.strip():
            raise ValueError("job_type is required")
        if not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be between 1 and 10")
        existing = self._store.get_by_idempotency_key(key)
        if existing:
            return existing, False

        timestamp = _aware(now)
        job = BackgroundJob(
            id=uuid4(),
            idempotency_key=key,
            job_type=job_type.strip(),
            payload=MappingProxyType(dict(payload)),
            status=JobStatus.QUEUED,
            attempts=0,
            max_attempts=max_attempts,
            available_at=timestamp,
        )
        self._store.insert(job)
        return job, True

    def claim(
        self,
        job_id: UUID,
        *,
        worker_id: str,
        now: datetime | None = None,
    ) -> BackgroundJob:
        timestamp = _aware(now)
        job = self._required(job_id)
        if job.status is not JobStatus.QUEUED or job.available_at > timestamp:
            raise JobStateError("job is not available for claim")
        claimed = replace(
            job,
            status=JobStatus.RUNNING,
            attempts=job.attempts + 1,
            claimed_by=worker_id.strip() or "anonymous-worker",
            claimed_at=timestamp,
            error_summary=None,
        )
        self._store.replace(claimed)
        return claimed

    def complete(
        self,
        job_id: UUID,
        *,
        worker_id: str,
        now: datetime | None = None,
    ) -> BackgroundJob:
        job = self._owned_running(job_id, worker_id)
        completed = replace(job, status=JobStatus.SUCCEEDED, completed_at=_aware(now))
        self._store.replace(completed)
        return completed

    def fail(
        self,
        job_id: UUID,
        *,
        worker_id: str,
        error_summary: str,
        retry_delay: timedelta = timedelta(seconds=5),
        now: datetime | None = None,
    ) -> BackgroundJob:
        timestamp = _aware(now)
        job = self._owned_running(job_id, worker_id)
        retry = job.attempts < job.max_attempts
        failed = replace(
            job,
            status=JobStatus.QUEUED if retry else JobStatus.FAILED,
            available_at=timestamp + retry_delay if retry else job.available_at,
            claimed_by=None,
            claimed_at=None,
            completed_at=None if retry else timestamp,
            error_summary=error_summary.strip()[:500] or "unspecified failure",
        )
        self._store.replace(failed)
        return failed

    def _required(self, job_id: UUID) -> BackgroundJob:
        job = self._store.get(job_id)
        if job is None:
            raise JobStateError("job does not exist")
        return job

    def _owned_running(self, job_id: UUID, worker_id: str) -> BackgroundJob:
        job = self._required(job_id)
        if job.status is not JobStatus.RUNNING or job.claimed_by != worker_id:
            raise JobStateError("job is not owned by this worker")
        return job


def _aware(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("job timestamps must be timezone-aware")
    return timestamp

