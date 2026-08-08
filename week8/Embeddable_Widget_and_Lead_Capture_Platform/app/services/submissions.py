from __future__ import annotations

from typing import Any
from uuid import UUID
from app.core.errors import OriginDenied, RateLimitExceeded
from app.core.security import hash_ip
from app.domain.types import PublicWidget, SubmissionResult
from app.rate_limit.base import RateLimiter
from app.repositories.submission_store import SubmissionStore
from app.services.field_validation import validate_widget_fields
from app.services.geo import GeoEnrichmentService


class SubmissionService:
    def __init__(self, *, store: SubmissionStore, rate_limiter: RateLimiter,
                 geo_service: GeoEnrichmentService, ip_hash_salt: str):
        self.store = store
        self.rate_limiter = rate_limiter
        self.geo_service = geo_service
        self.ip_hash_salt = ip_hash_salt

    async def submit(self, *, widget: PublicWidget, origin: str, client_ip: str,
                     user_agent: str | None, idempotency_key: UUID,
                     submitted_fields: dict[str, Any], honeypot: str = "") -> SubmissionResult:
        if origin not in widget.allowed_origins:
            raise OriginDenied("This origin is not allowed for this widget.")

        existing = await self.store.get_existing(widget.id, idempotency_key)
        if existing:
            return SubmissionResult(status="stored", submission=existing, duplicate=True)

        decision = await self.rate_limiter.check(widget.id, client_ip)
        if not decision.allowed:
            raise RateLimitExceeded(decision.retry_after)

        # Silent spam drop: count it against the limiter, do not enrich/store/notify.
        if honeypot.strip():
            return SubmissionResult(status="accepted_spam_drop")

        clean = validate_widget_fields(widget.fields, submitted_fields)
        geo = await self.geo_service.enrich(client_ip)
        stored, duplicate = await self.store.store_submission_and_job(
            widget=widget,
            idempotency_key=idempotency_key,
            payload=clean,
            origin=origin,
            ip_hash=hash_ip(client_ip, self.ip_hash_salt),
            user_agent=user_agent,
            geo=geo,
        )
        return SubmissionResult(status="stored", submission=stored, duplicate=duplicate)
