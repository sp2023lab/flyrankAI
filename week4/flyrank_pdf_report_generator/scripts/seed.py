import argparse
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.database import SessionLocal, ensure_schema
from app.models import Order

STATUSES = ("paid", "pending", "refunded", "cancelled")


def seed(count: int) -> None:
    ensure_schema()
    db = SessionLocal()
    try:
        now = datetime.now(UTC)
        orders = []
        for index in range(count):
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
        total = db.scalar(select(func.count(Order.id))) or 0
        print(f"Inserted {count} orders. Database now contains {int(total)} orders.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo order data")
    parser.add_argument("--count", type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.count <= 5000:
        raise SystemExit("--count must be between 1 and 5000")
    seed(args.count)
