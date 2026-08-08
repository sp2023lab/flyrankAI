import pytest
from starlette.requests import Request

from app.api.http import read_json_limited
from app.core.errors import InvalidSubmission, PayloadTooLarge


def make_request(body: bytes, content_length: str | None = None):
    sent = False
    headers = []
    if content_length is not None:
        headers.append((b"content-length", content_length.encode()))
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "POST", "scheme": "http", "path": "/", "raw_path": b"/",
        "query_string": b"", "headers": headers, "client": ("127.0.0.1", 1234),
        "server": ("test", 80),
    }
    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}
    return Request(scope, receive)


@pytest.mark.asyncio
async def test_streaming_body_limit_rejects_oversized_body():
    request = make_request(b"{\"x\":\"1234567890\"}")
    with pytest.raises(PayloadTooLarge):
        await read_json_limited(request, 8)


@pytest.mark.asyncio
async def test_declared_body_limit_rejects_before_parse():
    request = make_request(b"{}", content_length="999")
    with pytest.raises(PayloadTooLarge):
        await read_json_limited(request, 8)


@pytest.mark.asyncio
async def test_malformed_json_is_clean_invalid_submission():
    request = make_request(b"{not-json}")
    with pytest.raises(InvalidSubmission):
        await read_json_limited(request, 1024)
