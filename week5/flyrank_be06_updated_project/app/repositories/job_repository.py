from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReportJob


class JobRepository:
    @staticmethod
    def add(db: Session, job: ReportJob) -> ReportJob:
        db.add(job)
        db.flush()
        return job

    @staticmethod
    def get(db: Session, job_id: str) -> ReportJob | None:
        return db.get(ReportJob, job_id)

    @staticmethod
    def mark_running(db: Session, job: ReportJob, started_at: datetime) -> None:
        job.status = "running"
        job.started_at = started_at
        job.error = None

    @staticmethod
    def mark_completed(
        db: Session, job: ReportJob, report_id: str, completed_at: datetime
    ) -> None:
        job.status = "completed"
        job.report_id = report_id
        job.completed_at = completed_at
        job.error = None

    @staticmethod
    def mark_failed(db: Session, job: ReportJob, error: str, completed_at: datetime) -> None:
        job.status = "failed"
        job.completed_at = completed_at
        job.error = error[:2000]

    @staticmethod
    def list_recent(db: Session, limit: int = 50) -> list[ReportJob]:
        statement = select(ReportJob).order_by(ReportJob.requested_at.desc()).limit(limit)
        return list(db.scalars(statement))
