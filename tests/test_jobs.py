from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marginscout_public.jobs import (  # noqa: E402
    InMemoryJobStore,
    JobService,
    JobStateError,
    JobStatus,
)


NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


class JobServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryJobStore()
        self.service = JobService(self.store)

    def test_enqueue_is_idempotent(self) -> None:
        first, created_first = self.service.enqueue(
            idempotency_key="source:window-1",
            job_type="source_sync",
            payload={"source_id": "synthetic"},
            now=NOW,
        )
        second, created_second = self.service.enqueue(
            idempotency_key="source:window-1",
            job_type="source_sync",
            payload={"source_id": "changed-but-ignored"},
            now=NOW,
        )

        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.id, second.id)

    def test_claim_and_complete_require_worker_ownership(self) -> None:
        job, _ = self.service.enqueue(
            idempotency_key="assessment:1",
            job_type="lead_assessment",
            payload={},
            now=NOW,
        )
        claimed = self.service.claim(job.id, worker_id="worker-a", now=NOW)
        self.assertEqual(claimed.status, JobStatus.RUNNING)
        self.assertEqual(claimed.attempts, 1)

        with self.assertRaises(JobStateError):
            self.service.complete(job.id, worker_id="worker-b", now=NOW)

        completed = self.service.complete(job.id, worker_id="worker-a", now=NOW)
        self.assertEqual(completed.status, JobStatus.SUCCEEDED)

    def test_failure_retries_then_becomes_terminal(self) -> None:
        job, _ = self.service.enqueue(
            idempotency_key="assessment:retry",
            job_type="lead_assessment",
            payload={},
            max_attempts=2,
            now=NOW,
        )
        self.service.claim(job.id, worker_id="worker-a", now=NOW)
        retried = self.service.fail(
            job.id,
            worker_id="worker-a",
            error_summary="temporary",
            retry_delay=timedelta(seconds=1),
            now=NOW,
        )
        self.assertEqual(retried.status, JobStatus.QUEUED)

        claimed_again = self.service.claim(
            job.id,
            worker_id="worker-a",
            now=NOW + timedelta(seconds=1),
        )
        self.assertEqual(claimed_again.attempts, 2)
        terminal = self.service.fail(
            job.id,
            worker_id="worker-a",
            error_summary="permanent",
            now=NOW + timedelta(seconds=1),
        )
        self.assertEqual(terminal.status, JobStatus.FAILED)


if __name__ == "__main__":
    unittest.main()

