from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from app.api.dependencies import require_tenant_id
from app.db.models import Submission, Widget
from app.db.session import SessionFactory

router = APIRouter(tags=["dashboard"])


def _apply_date_filters(stmt, from_dt: datetime | None, to_dt: datetime | None):
    if from_dt is not None:
        stmt = stmt.where(Submission.created_at >= from_dt)
    if to_dt is not None:
        stmt = stmt.where(Submission.created_at <= to_dt)
    return stmt


@router.get("/api/v1/submissions")
async def list_submissions(
    widget_id: UUID | None = None,
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: UUID = Depends(require_tenant_id),
):
    filters = [Submission.tenant_id == tenant_id]
    if widget_id is not None:
        filters.append(Submission.widget_id == widget_id)

    async with SessionFactory() as session:
        count_stmt = select(func.count(Submission.id)).where(*filters)
        count_stmt = _apply_date_filters(count_stmt, from_dt, to_dt)
        total = int((await session.scalar(count_stmt)) or 0)

        stmt = (
            select(Submission)
            .where(*filters)
            .order_by(Submission.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        stmt = _apply_date_filters(stmt, from_dt, to_dt)
        items = list((await session.scalars(stmt)).all())

    return {
        "items": [
            {
                "id": row.id,
                "widget_id": row.widget_id,
                "payload": row.payload,
                "origin": row.origin,
                "country_code": row.country_code,
                "country": row.country,
                "city": row.city,
                "geo_provider": row.geo_provider,
                "created_at": row.created_at,
            }
            for row in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/api/v1/dashboard/summary")
async def dashboard_summary(
    tenant_id: UUID = Depends(require_tenant_id),
):
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    async with SessionFactory() as session:
        total_submissions = int(
            (await session.scalar(
                select(func.count(Submission.id)).where(
                    Submission.tenant_id == tenant_id
                )
            ))
            or 0
        )

        last_24_hours = int(
            (await session.scalar(
                select(func.count(Submission.id)).where(
                    Submission.tenant_id == tenant_id,
                    Submission.created_at >= since,
                )
            ))
            or 0
        )

        widgets = int(
            (await session.scalar(
                select(func.count(Widget.id)).where(
                    Widget.tenant_id == tenant_id
                )
            ))
            or 0
        )

    return {
        "total_submissions": total_submissions,
        "last_24_hours": last_24_hours,
        "widgets": widgets,
    }


@router.get("/api/v1/dashboard/geo")
async def dashboard_geo(
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    tenant_id: UUID = Depends(require_tenant_id),
):
    stmt = (
        select(
            Submission.country_code,
            Submission.country,
            func.count(Submission.id).label("count"),
        )
        .where(
            Submission.tenant_id == tenant_id,
            Submission.country_code.is_not(None),
        )
        .group_by(Submission.country_code, Submission.country)
        .order_by(func.count(Submission.id).desc())
    )
    stmt = _apply_date_filters(stmt, from_dt, to_dt)

    async with SessionFactory() as session:
        rows = (await session.execute(stmt)).all()

    return {
        "countries": [
            {
                "country_code": country_code,
                "country": country,
                "count": int(count),
            }
            for country_code, country, count in rows
        ]
    }


@router.get("/api/v1/dashboard/widgets/{widget_id}/stats")
async def widget_stats(
    widget_id: UUID,
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    tenant_id: UUID = Depends(require_tenant_id),
):
    async with SessionFactory() as session:
        widget = await session.scalar(
            select(Widget).where(
                Widget.id == widget_id,
                Widget.tenant_id == tenant_id,
            )
        )
        if widget is None:
            raise HTTPException(status_code=404, detail="Widget not found")

        total_stmt = select(func.count(Submission.id)).where(
            Submission.tenant_id == tenant_id,
            Submission.widget_id == widget_id,
        )
        total_stmt = _apply_date_filters(total_stmt, from_dt, to_dt)
        total = int((await session.scalar(total_stmt)) or 0)

        day_expr = func.date(Submission.created_at)
        daily_stmt = (
            select(day_expr.label("date"), func.count(Submission.id).label("count"))
            .where(
                Submission.tenant_id == tenant_id,
                Submission.widget_id == widget_id,
            )
            .group_by(day_expr)
            .order_by(day_expr)
        )
        daily_stmt = _apply_date_filters(daily_stmt, from_dt, to_dt)
        daily_rows = (await session.execute(daily_stmt)).all()

    return {
        "widget_id": widget_id,
        "total_submissions": total,
        "by_day": [
            {"date": str(day), "count": int(count)}
            for day, count in daily_rows
        ],
    }