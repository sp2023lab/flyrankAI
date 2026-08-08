from __future__ import annotations

import re
from typing import Any
from app.core.errors import InvalidSubmission

_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_widget_fields(configured_fields: list[dict], submitted: dict[str, Any]) -> dict[str, str]:
    allowed = {field["name"]: field for field in configured_fields}
    errors: list[dict] = []

    for key in submitted:
        if key not in allowed:
            errors.append({"field": key, "reason": "unexpected_field"})

    clean: dict[str, str] = {}
    for name, spec in allowed.items():
        value = submitted.get(name)
        if value is None or value == "":
            if spec.get("required", False):
                errors.append({"field": name, "reason": "required"})
            continue
        if not isinstance(value, str):
            errors.append({"field": name, "reason": "must_be_string"})
            continue
        max_length = int(spec.get("max_length", 254))
        if len(value) > max_length:
            errors.append({"field": name, "reason": "too_long", "max_length": max_length})
            continue
        if spec.get("type") == "email" and not _EMAIL.fullmatch(value):
            errors.append({"field": name, "reason": "invalid_email"})
            continue
        clean[name] = value

    if errors:
        raise InvalidSubmission("The submitted fields are invalid.", details=errors)
    return clean
