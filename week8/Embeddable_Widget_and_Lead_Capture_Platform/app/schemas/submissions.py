from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class SubmissionBody(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    fields: dict[str, Any]
    honeypot: str = Field(default="", alias="_website", max_length=500)
