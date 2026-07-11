from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    database: str


class ReportRequest(BaseModel):
    report_type: Literal["sales_summary"] = "sales_summary"
    title: str = Field(default="Sales Summary Report", min_length=3, max_length=200)


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: Literal["queued", "running", "completed", "failed"]
    report_type: str
    title: str
    requested_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    report_id: str | None
    error: str | None
    status_url: str | None = None
    download_url: str | None = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_type: str
    title: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    created_at: datetime
    download_url: str | None = None


class SeedRequest(BaseModel):
    count: int = Field(default=60, ge=1, le=500)


class SeedResponse(BaseModel):
    inserted: int
    total_orders: int


class StatusMetric(BaseModel):
    status: str
    order_count: int
    revenue: Decimal


class DailyMetric(BaseModel):
    date: str
    order_count: int
    revenue: Decimal


class SalesSummary(BaseModel):
    total_orders: int
    gross_revenue: Decimal
    average_order_value: Decimal
    by_status: list[StatusMetric]
    daily: list[DailyMetric]
