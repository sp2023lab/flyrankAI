from __future__ import annotations

import json
from fastapi import Request
from app.core.errors import PayloadTooLarge


async def read_json_limited(request: Request, max_bytes: int) -> dict:
    raw_length = request.headers.get("content-length")
    if raw_length:
        try:
            if int(raw_length) > max_bytes:
                raise PayloadTooLarge(f"Request body exceeds {max_bytes} bytes.")
        except ValueError:
            pass

    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > max_bytes:
            raise PayloadTooLarge(f"Request body exceeds {max_bytes} bytes.")
        chunks.append(chunk)
    try:
        data = json.loads(b"".join(chunks) or b"{}")
    except json.JSONDecodeError as exc:
        from app.core.errors import InvalidSubmission
        raise InvalidSubmission("Malformed JSON.") from exc
    if not isinstance(data, dict):
        from app.core.errors import InvalidSubmission
        raise InvalidSubmission("Request body must be a JSON object.")
    return data


def cors_headers(origin: str) -> dict[str, str]:
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Idempotency-Key",
        "Access-Control-Max-Age": "600",
        "Vary": "Origin",
    }
