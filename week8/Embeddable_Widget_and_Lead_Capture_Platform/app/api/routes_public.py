from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError

from app.api.dependencies import get_submission_service, get_submission_store
from app.api.http import cors_headers, read_json_limited
from app.core.config import get_settings
from app.core.errors import AppError, OriginDenied, RateLimitExceeded, WidgetNotFound
from app.schemas.submissions import SubmissionBody
from app.services.submissions import SubmissionService

router = APIRouter(prefix="/public/v1/widgets", tags=["public"])
settings = get_settings()


def _error(exc: AppError, headers: dict[str, str] | None = None):
    payload = {"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
    response_headers = dict(headers or {})
    if isinstance(exc, RateLimitExceeded): response_headers["Retry-After"] = str(exc.retry_after)
    return JSONResponse(status_code=exc.status_code, content=payload, headers=response_headers)


def _client_ip(request: Request) -> str:
    if settings.trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded: return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.options("/{public_id}/submissions")
async def submissions_preflight(public_id: UUID, request: Request, store=Depends(get_submission_store)):
    widget = await store.get_public_widget(public_id)
    if not widget: return _error(WidgetNotFound("Widget not found."))
    origin = request.headers.get("origin", "")
    if origin not in widget.allowed_origins: return _error(OriginDenied("Origin not allowed."))
    return Response(status_code=204, headers=cors_headers(origin))


@router.post("/{public_id}/submissions")
async def create_submission(
    public_id: UUID,
    request: Request,
    idempotency_key: UUID = Header(..., alias="Idempotency-Key"),
    store=Depends(get_submission_store),
    service: SubmissionService = Depends(get_submission_service),
):
    widget = await store.get_public_widget(public_id)
    if not widget: return _error(WidgetNotFound("Widget not found."))
    origin = request.headers.get("origin", "")
    if origin not in widget.allowed_origins: return _error(OriginDenied("Origin not allowed."))
    headers = cors_headers(origin)
    try:
        raw = await read_json_limited(request, settings.max_submission_body_bytes)
        body = SubmissionBody.model_validate(raw)
        result = await service.submit(
            widget=widget, origin=origin, client_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent"), idempotency_key=idempotency_key,
            submitted_fields=body.fields, honeypot=body.honeypot,
        )
    except ValidationError as exc:
        from app.core.errors import InvalidSubmission
        return _error(InvalidSubmission("Invalid request shape.", details=exc.errors(include_url=False)), headers)
    except AppError as exc:
        return _error(exc, headers)

    if result.status == "accepted_spam_drop":
        return JSONResponse(status_code=202, content={"status": "accepted"}, headers=headers)
    status = 200 if result.duplicate else 201
    return JSONResponse(status_code=status, content={
        "status": "stored", "submission_id": str(result.submission.id), "duplicate": result.duplicate
    }, headers=headers)


@router.get("/{public_id}/config")
async def public_config(public_id: UUID, request: Request, store=Depends(get_submission_store)):
    widget = await store.get_public_widget(public_id)
    if not widget: return _error(WidgetNotFound("Widget not found."))
    origin = request.headers.get("origin", "")
    if origin and origin not in widget.allowed_origins: return _error(OriginDenied("Origin not allowed."))
    headers = {"Cache-Control": "public, max-age=60, stale-while-revalidate=300"}
    if origin: headers.update(cors_headers(origin))
    return JSONResponse(content={
        "public_id": str(widget.public_id), "type": widget.widget_type, "title": widget.title,
        "description": widget.description, "button_text": widget.button_text,
        "fields": widget.fields, "display_options": widget.display_options,
    }, headers=headers)
