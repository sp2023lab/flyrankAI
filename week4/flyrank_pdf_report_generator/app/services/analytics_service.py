from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import DailyMetric, SalesSummary, StatusMetric

ZERO = Decimal("0.00")


def _as_decimal(value: object | None) -> Decimal:
    if value is None:
        return ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"))


def build_sales_summary(db: Session, days: int = 14) -> SalesSummary:
    totals = db.execute(
        select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0),
            func.coalesce(func.avg(Order.total_amount), 0),
        )
    ).one()

    status_rows = db.execute(
        select(
            Order.status,
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0),
        )
        .group_by(Order.status)
        .order_by(Order.status)
    ).all()

    cutoff = datetime.now(UTC) - timedelta(days=days)
    day_expression = func.date(Order.created_at)
    daily_rows = db.execute(
        select(
            day_expression.label("day"),
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0),
        )
        .where(Order.created_at >= cutoff)
        .group_by(day_expression)
        .order_by(day_expression)
    ).all()

    return SalesSummary(
        total_orders=int(totals[0] or 0),
        gross_revenue=_as_decimal(totals[1]),
        average_order_value=_as_decimal(totals[2]),
        by_status=[
            StatusMetric(status=row[0], order_count=int(row[1]), revenue=_as_decimal(row[2]))
            for row in status_rows
        ],
        daily=[
            DailyMetric(date=str(row[0]), order_count=int(row[1]), revenue=_as_decimal(row[2]))
            for row in daily_rows
        ],
    )
