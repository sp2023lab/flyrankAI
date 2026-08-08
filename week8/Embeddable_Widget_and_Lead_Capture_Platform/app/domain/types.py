from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class PublicWidget:
    id: UUID
    public_id: UUID
    tenant_id: UUID
    widget_type: str
    title: str
    description: str | None
    button_text: str
    fields: list[dict[str, Any]]
    display_options: dict[str, Any]
    allowed_origins: list[str]
    is_active: bool = True


@dataclass(slots=True)
class GeoLocation:
    country_code: str | None = None
    country: str | None = None
    city: str | None = None
    provider: str | None = None


@dataclass(slots=True)
class StoredSubmission:
    id: UUID
    widget_id: UUID
    tenant_id: UUID
    idempotency_key: UUID
    payload: dict[str, Any]
    country_code: str | None = None
    country: str | None = None
    city: str | None = None
    geo_provider: str | None = None
    created_at: datetime | None = None


@dataclass(slots=True)
class SubmissionResult:
    status: str
    submission: StoredSubmission | None = None
    duplicate: bool = False
