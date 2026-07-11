from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import SalesSummary, SeedRequest, SeedResponse
from app.services.analytics_service import build_sales_summary

router = APIRouter(prefix="/api/v1/demo", tags=["demo data"])
DbSession = Annotated[Session, Depends(get_db)]
STATUSES = ("paid", "pending", "refunded", "cancelled")


@router.post("/orders/seed", response_model=SeedResponse)
def seed_orders(payload: SeedRequest, db: DbSession) -> SeedResponse:
    now = datetime.now(UTC)
    orders = []
    for index in range(payload.count):
        amount = Decimal("18.50") + Decimal((index * 17) % 190) + Decimal(index % 100) / 100
        orders.append(
            Order(
                customer_name=f"Customer {index + 1:03d}",
                status=STATUSES[index % len(STATUSES)],
                total_amount=amount.quantize(Decimal("0.01")),
                created_at=now - timedelta(days=index % 12, hours=index % 24),
            )
        )
    db.add_all(orders)
    db.commit()
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    return SeedResponse(inserted=payload.count, total_orders=int(total_orders))


@router.get("/orders/summary", response_model=SalesSummary)
def preview_summary(db: DbSession) -> SalesSummary:
    return build_sales_summary(db)
