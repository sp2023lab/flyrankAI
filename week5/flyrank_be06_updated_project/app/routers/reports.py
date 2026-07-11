from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ReportJob
from app.repositories.job_repository import JobRepository
from app.repositories.report_repository import ReportRepository
from app.schemas import JobResponse, ReportRequest, ReportResponse
from app.tasks import generate_sales_report

router = APIRouter(prefix="/api/v1", tags=["reports"])
settings = get_settings()
DbSession = Annotated[Session, Depends(get_db)]


def _job_response(job: ReportJob, request: Request) -> JobResponse:
    response = JobResponse.model_validate(job)
    response.status_url = str(request.url_for("get_job", job_id=job.id))
    if job.report_id:
        response.download_url = str(request.url_for("download_report", report_id=job.report_id))
    return response


@router.post("/reports", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def request_report(payload: ReportRequest, request: Request, db: DbSession) -> JobResponse:
    job = ReportJob(
        id=str(uuid4()),
        status="queued",
        report_type=payload.report_type,
        title=payload.title,
    )
    JobRepository.add(db, job)
    db.commit()
    try:
        generate_sales_report.delay(job.id)
    except Exception as exc:
        job.status = "failed"
        job.error = f"Could not enqueue background job: {exc}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The report worker queue is unavailable.",
        ) from exc
    return _job_response(job, request)


@router.get("/jobs/{job_id}", response_model=JobResponse, name="get_job")
def get_job(job_id: str, request: Request, db: DbSession) -> JobResponse:
    job = JobRepository.get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Report job not found")
    return _job_response(job, request)


@router.get("/reports", response_model=list[ReportResponse])
def list_reports(request: Request, db: DbSession) -> list[ReportResponse]:
    responses = []
    for report in ReportRepository.list_recent(db):
        item = ReportResponse.model_validate(report)
        item.download_url = str(request.url_for("download_report", report_id=report.id))
        responses.append(item)
    return responses


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, request: Request, db: DbSession) -> ReportResponse:
    report = ReportRepository.get(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    response = ReportResponse.model_validate(report)
    response.download_url = str(request.url_for("download_report", report_id=report.id))
    return response


@router.get("/reports/{report_id}/download", name="download_report")
def download_report(report_id: str, db: DbSession) -> FileResponse:
    report = ReportRepository.get(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    artifact_root = Path(settings.artifacts_dir).resolve()
    file_path = (artifact_root / report.file_path).resolve()
    if artifact_root not in file_path.parents or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Report artifact is unavailable")
    return FileResponse(path=file_path, media_type=report.mime_type, filename=report.file_name)
