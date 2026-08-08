from __future__ import annotations

from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class WidgetField(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_]{0,49}$")
    label: str = Field(min_length=1, max_length=80)
    type: Literal["text", "email", "textarea"]
    required: bool = False
    max_length: int = Field(default=254, ge=1, le=2000)


class WidgetCreate(BaseModel):
    widget_type: Literal["signup_form", "contact_form"]
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    button_text: str = Field(default="Submit", min_length=1, max_length=60)
    fields: list[WidgetField] = Field(min_length=1, max_length=12)
    display_options: dict[str, Any] = Field(default_factory=dict)
    allowed_origins: list[str] = Field(min_length=1, max_length=20)

    @field_validator("allowed_origins")
    @classmethod
    def exact_http_origins(cls, values: list[str]):
        for value in values:
            if not (value.startswith("http://") or value.startswith("https://")):
                raise ValueError("allowed origins must be exact http(s) origins")
            if value.endswith("/"):
                raise ValueError("allowed origins must not contain a trailing slash")
        return list(dict.fromkeys(values))


class WidgetOut(BaseModel):
    id: UUID
    public_id: UUID
    widget_type: str
    title: str
    description: str | None
    button_text: str
    fields: list[dict]
    display_options: dict
    allowed_origins: list[str]
    is_active: bool

    model_config = {"from_attributes": True}
