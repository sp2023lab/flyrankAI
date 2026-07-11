from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.celery_app import celery_app
from app.config import get_settings
from app.database import SessionLocal, ensure_schema
from app.models import ReportArtifact, ReportJob
from app.repositories.job_repository import JobRepository
from app.repositories.report_repository import ReportRepository
from app.services.analytics_service import build_sales_summary
from app.services.pdf_renderer import render_sales_report

settings = get_settings()


def _utc_now() -> datetime:
    return datetime.now(UTC)


@celery_app.task(name="app.tasks.generate_sales_report")
def generate_sales_report(job_id: str) -> str:
    ensure_schema()
    db = SessionLocal()
    try:
        job = JobRepository.get(db, job_id)
        if job is None:
            raise ValueError(f"Unknown report job: {job_id}")
        if job.status == "completed" and job.report_id:
            return job.report_id

        JobRepository.mark_running(db, job, _utc_now())
        db.commit()

        summary = build_sales_summary(db)
        report_id = str(uuid4())
        file_name = f"sales-summary-{report_id}.pdf"
        output_path = Path(settings.artifacts_dir) / file_name
        generated_at = _utc_now()
        file_size = render_sales_report(output_path, job.title, summary, generated_at)

        artifact = ReportArtifact(
            id=report_id,
            report_type=job.report_type,
            title=job.title,
            file_name=file_name,
            file_path=file_name,
            mime_type="application/pdf",
            file_size_bytes=file_size,
            created_at=generated_at,
        )
        ReportRepository.add(db, artifact)
        JobRepository.mark_completed(db, job, report_id, _utc_now())
        db.commit()
        return report_id
    except Exception as exc:
        db.rollback()
        failed_job = JobRepository.get(db, job_id)
        if failed_job is not None:
            JobRepository.mark_failed(db, failed_job, str(exc), _utc_now())
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.enqueue_scheduled_report")
def enqueue_scheduled_report() -> str:
    ensure_schema()
    db = SessionLocal()
    try:
        job = ReportJob(
            id=str(uuid4()),
            status="queued",
            report_type="sales_summary",
            title=f"Scheduled Sales Summary - {_utc_now().date().isoformat()}",
        )
        JobRepository.add(db, job)
        db.commit()
        generate_sales_report.delay(job.id)
        return job.id
    finally:
        db.close()
