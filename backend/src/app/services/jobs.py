import uuid
from datetime import UTC, datetime
from typing import Any

_jobs: dict[str, dict[str, Any]] = {}


def create_job() -> str:
    """Create a new job record and return its id."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending",
        "stage": "",
        "current": 0,
        "total": 0,
        "started_at": datetime.now(UTC).isoformat(),
        "finished_at": None,
        "error": None,
    }
    return job_id


def update_job(job_id: str, **fields: Any) -> None:
    """Merge *fields* into an existing job record."""
    if job_id in _jobs:
        _jobs[job_id].update(fields)


def get_job(job_id: str) -> dict[str, Any] | None:
    """Return the job dict, or None if not found."""
    return _jobs.get(job_id)
