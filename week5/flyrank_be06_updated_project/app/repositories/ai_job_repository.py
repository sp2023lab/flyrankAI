from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session

from app.models import AIJob


class AIJobRepository:
    @staticmethod
    def add(db: Session, job: AIJob) -> AIJob:
        db.add(job)
        db.flush()
        return job

    @staticmethod
    def get(db: Session, job_id: str) -> AIJob | None:
        return db.get(AIJob, job_id)

    @staticmethod
    def get_by_idempotency_key(db: Session, key: str) -> AIJob | None:
        return db.scalar(select(AIJob).where(AIJob.idempotency_key == key))

    @staticmethod
    def claim(
        db: Session,
        job_id: str,
        *,
        now: datetime,
        stale_after_seconds: int,
    ) -> bool:
        stale_before = now - timedelta(seconds=stale_after_seconds)
        claimable = or_(
            AIJob.status.in_(("queued", "retrying")),
            and_(AIJob.status == "running", AIJob.started_at < stale_before),
        )
        result = db.execute(
            update(AIJob)
            .where(AIJob.id == job_id, claimable, AIJob.attempts < AIJob.max_attempts)
            .values(
                status="running",
                attempts=AIJob.attempts + 1,
                started_at=now,
                updated_at=now,
                error=None,
            )
        )
        return result.rowcount == 1

    @staticmethod
    def mark_retrying(db: Session, job: AIJob, error: str, now: datetime) -> None:
        job.status = "retrying"
        job.error = error[:2000]
        job.updated_at = now

    @staticmethod
    def mark_completed(db: Session, job: AIJob, result_json: str, now: datetime) -> None:
        job.status = "completed"
        job.result_json = result_json
        job.error = None
        job.completed_at = now
        job.updated_at = now

    @staticmethod
    def mark_failed(db: Session, job: AIJob, error: str, now: datetime) -> None:
        job.status = "failed"
        job.error = error[:2000]
        job.completed_at = now
        job.updated_at = now
