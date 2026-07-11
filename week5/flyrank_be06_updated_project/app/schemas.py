import json
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class SummarizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=20_000)


class SummaryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bullets: list[str] = Field(min_length=3, max_length=3)

    @field_validator("bullets")
    @classmethod
    def validate_bullets(cls, bullets: list[str]) -> list[str]:
        normalized = [bullet.strip() for bullet in bullets]
        if any(not bullet for bullet in normalized):
            raise ValueError("Summary bullets cannot be empty.")
        return normalized


class AIJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: Literal["queued", "running", "retrying", "completed", "failed"]
    feature: str
    attempts: int
    max_attempts: int
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None
    result: SummaryResult | None = None
    status_url: str | None = None

    @classmethod
    def from_job(cls, job: object, *, status_url: str | None = None) -> "AIJobResponse":
        result_json = getattr(job, "result_json", None)
        result = SummaryResult.model_validate(json.loads(result_json)) if result_json else None
        return cls(
            id=getattr(job, "id"),
            status=getattr(job, "status"),
            feature=getattr(job, "feature"),
            attempts=getattr(job, "attempts"),
            max_attempts=getattr(job, "max_attempts"),
            created_at=getattr(job, "created_at"),
            updated_at=getattr(job, "updated_at"),
            started_at=getattr(job, "started_at"),
            completed_at=getattr(job, "completed_at"),
            error=getattr(job, "error"),
            result=result,
            status_url=status_url,
        )
