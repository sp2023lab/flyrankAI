from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.db.models import NotificationJob, Submission, Widget
from app.domain.types import GeoLocation, PublicWidget, StoredSubmission


class SubmissionStore(Protocol):
    async def get_public_widget(self, public_id: UUID) -> PublicWidget | None: ...
    async def get_existing(self, widget_id: UUID, idempotency_key: UUID) -> StoredSubmission | None: ...
    async def store_submission_and_job(self, *, widget: PublicWidget, idempotency_key: UUID,
        payload: dict[str, Any], origin: str, ip_hash: str, user_agent: str | None,
        geo: GeoLocation | None) -> tuple[StoredSubmission, bool]: ...


def _widget(row: Widget) -> PublicWidget:
    return PublicWidget(
        id=row.id, public_id=row.public_id, tenant_id=row.tenant_id, widget_type=row.widget_type,
        title=row.title, description=row.description, button_text=row.button_text, fields=row.fields,
        display_options=row.display_options, allowed_origins=row.allowed_origins, is_active=row.is_active,
    )


def _submission(row: Submission) -> StoredSubmission:
    return StoredSubmission(
        id=row.id, widget_id=row.widget_id, tenant_id=row.tenant_id, idempotency_key=row.idempotency_key,
        payload=row.payload, country_code=row.country_code, country=row.country, city=row.city,
        geo_provider=row.geo_provider, created_at=row.created_at,
    )


class SqlAlchemySubmissionStore:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get_public_widget(self, public_id: UUID) -> PublicWidget | None:
        async with self.session_factory() as session:
            row = await session.scalar(select(Widget).where(Widget.public_id == public_id, Widget.is_active.is_(True)))
            return _widget(row) if row else None

    async def get_existing(self, widget_id: UUID, idempotency_key: UUID) -> StoredSubmission | None:
        async with self.session_factory() as session:
            row = await session.scalar(select(Submission).where(
                Submission.widget_id == widget_id, Submission.idempotency_key == idempotency_key
            ))
            return _submission(row) if row else None

    async def store_submission_and_job(self, *, widget: PublicWidget, idempotency_key: UUID,
        payload: dict[str, Any], origin: str, ip_hash: str, user_agent: str | None,
        geo: GeoLocation | None) -> tuple[StoredSubmission, bool]:
        async with self.session_factory() as session:
            try:
                async with session.begin():
                    row = Submission(
                        tenant_id=widget.tenant_id, widget_id=widget.id, idempotency_key=idempotency_key,
                        payload=payload, origin=origin, ip_hash=ip_hash, user_agent=(user_agent or "")[:500] or None,
                        country_code=geo.country_code if geo else None, country=geo.country if geo else None,
                        city=geo.city if geo else None, geo_provider=geo.provider if geo else None,
                    )
                    session.add(row)
                    await session.flush()
                    session.add(NotificationJob(submission_id=row.id, status="pending"))
                await session.refresh(row)
                return _submission(row), False
            except IntegrityError:
                await session.rollback()
                existing = await session.scalar(select(Submission).where(
                    Submission.widget_id == widget.id, Submission.idempotency_key == idempotency_key
                ))
                if not existing: raise
                return _submission(existing), True
