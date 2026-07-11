from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import AIJob
from app.repositories.ai_job_repository import AIJobRepository
from app.schemas import AIJobResponse, SummarizeRequest
from app.tasks import generate_ai_summary

router = APIRouter(prefix="/api/v1", tags=["ai jobs"])
settings = get_settings()
DbSession = Annotated[Session, Depends(get_db)]
IdempotencyKey = Annotated[
    str | None,
    Header(alias="Idempotency-Key", min_length=8, max_length=128),
]


def _response(job: AIJob, request: Request) -> AIJobResponse:
    status_url = str(request.url_for("get_ai_job", job_id=job.id))
    return AIJobResponse.from_job(job, status_url=status_url)


@router.post(
    "/summarize",
    response_model=AIJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_summary(
    payload: SummarizeRequest,
    request: Request,
    response: Response,
    db: DbSession,
    idempotency_key: IdempotencyKey = None,
) -> AIJobResponse:
    if idempotency_key:
        existing = AIJobRepository.get_by_idempotency_key(db, idempotency_key)
        if existing is not None:
            status_url = str(request.url_for("get_ai_job", job_id=existing.id))
            response.headers["Location"] = status_url
            response.headers["Retry-After"] = "2"
            return AIJobResponse.from_job(existing, status_url=status_url)

    job = AIJob(
        id=str(uuid4()),
        status="queued",
        feature="summarize",
        input_text=payload.text,
        max_attempts=settings.ai_job_max_attempts,
        idempotency_key=idempotency_key,
    )
    try:
        AIJobRepository.add(db, job)
        db.commit()
    except IntegrityError:
        db.rollback()
        if not idempotency_key:
            raise
        existing = AIJobRepository.get_by_idempotency_key(db, idempotency_key)
        if existing is None:
            raise
        status_url = str(request.url_for("get_ai_job", job_id=existing.id))
        response.headers["Location"] = status_url
        response.headers["Retry-After"] = "2"
        return AIJobResponse.from_job(existing, status_url=status_url)

    try:
        generate_ai_summary.delay(job.id)
    except Exception as exc:
        job.status = "failed"
        job.error = "The AI worker queue is unavailable."
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI worker queue is unavailable.",
        ) from exc

    status_url = str(request.url_for("get_ai_job", job_id=job.id))
    response.headers["Location"] = status_url
    response.headers["Retry-After"] = "2"
    return AIJobResponse.from_job(job, status_url=status_url)


@router.get("/ai-jobs/{job_id}", response_model=AIJobResponse, name="get_ai_job")
def get_ai_job(job_id: str, request: Request, db: DbSession) -> AIJobResponse:
    job = AIJobRepository.get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="AI job not found")
    return _response(job, request)
