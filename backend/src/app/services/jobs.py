import uuid
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session

from app.db import engine
from app.models.job import Job


def create_job() -> str:
    """Create a new job record in the database and return its id."""
    job_id = str(uuid.uuid4())
    with Session(engine) as session:
        job = Job(
            id=job_id,
            status="pending",
            stage="",
            current=0,
            total=0,
            started_at=datetime.now(UTC).isoformat(),
        )
        session.add(job)
        session.commit()
    return job_id


def update_job(job_id: str, **fields: Any) -> None:
    """Merge *fields* into the persisted job record."""
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)
        session.add(job)
        session.commit()


def get_job(job_id: str) -> dict[str, Any] | None:
    """Return the job as a plain dict, or None if not found."""
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job is None:
            return None
        return {
            "status": job.status,
            "stage": job.stage,
            "current": job.current,
            "total": job.total,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "error": job.error,
        }
