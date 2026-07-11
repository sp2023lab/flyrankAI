import asyncio
import logging

import httpx
import pytest

from app.ai.base import AICompletion, AIProviderError, AIProviderTimeout
from app.ai.groq_provider import GroqProvider
from app.main import app
from app.routers.summarize import resolve_ai_provider


class StubProvider:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls = 0

    async def complete(self, **_: object) -> AICompletion:
        response = self.responses[self.calls]
        self.calls += 1
        return AICompletion(
            content=response,
            input_tokens=10,
            output_tokens=20,
            model="test-model",
        )


@pytest.fixture(autouse=True)
def clear_ai_dependency_override():
    yield
    app.dependency_overrides.pop(resolve_ai_provider, None)


def test_summarize_returns_exactly_three_bullets(client):
    provider = StubProvider(
        ['{"bullets":["First finding","Second finding","Third finding"]}']
    )
    app.dependency_overrides[resolve_ai_provider] = lambda: provider

    response = client.post(
        "/api/v1/summarize",
        json={"text": "A long report containing three important findings."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "bullets": ["First finding", "Second finding", "Third finding"]
    }
    assert provider.calls == 1


def test_summarize_retries_once_after_malformed_output(client):
    provider = StubProvider(
        [
            '{"bullets":["Only one bullet"]}',
            '{"bullets":["One","Two","Three"]}',
        ]
    )
    app.dependency_overrides[resolve_ai_provider] = lambda: provider

    response = client.post(
        "/api/v1/summarize",
        json={"text": "Report text that should be summarized."},
    )

    assert response.status_code == 200
    assert response.json()["bullets"] == ["One", "Two", "Three"]
    assert provider.calls == 2


def test_summarize_returns_clean_error_after_two_invalid_outputs(client):
    provider = StubProvider(["not-json", '{"bullets":[]}'])
    app.dependency_overrides[resolve_ai_provider] = lambda: provider

    response = client.post(
        "/api/v1/summarize",
        json={"text": "Report text that should be summarized."},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The AI provider returned invalid structured output."
    }
    assert provider.calls == 2


def test_summarize_rejects_empty_text(client):
    response = client.post("/api/v1/summarize", json={"text": ""})
    assert response.status_code == 422


def _provider(
    transport: httpx.AsyncBaseTransport,
    *,
    max_retries: int = 1,
    api_key: str = "test-secret-key",
) -> GroqProvider:
    return GroqProvider(
        api_key=api_key,
        model="openai/gpt-oss-20b",
        timeout_seconds=1,
        max_retries=max_retries,
        retry_backoff_seconds=0,
        input_cost_per_million=0.075,
        output_cost_per_million=0.30,
        transport=transport,
    )


def _complete(provider: GroqProvider) -> AICompletion:
    return asyncio.run(
        provider.complete(
            feature="summarize",
            system_prompt="Summarize accurately.",
            user_prompt="Example report text.",
            schema={
                "type": "object",
                "properties": {
                    "bullets": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["bullets"],
                "additionalProperties": False,
            },
        )
    )


def test_groq_retries_429_then_logs_tokens_and_cost(caplog):
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, json={"error": "rate limited"}, request=request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"bullets":["One","Two","Three"]}'
                        }
                    }
                ],
                "usage": {"prompt_tokens": 100, "completion_tokens": 50},
            },
            request=request,
        )

    caplog.set_level(logging.INFO, logger="app.ai.groq_provider")
    result = _complete(_provider(httpx.MockTransport(handler)))

    assert calls == 2
    assert result.input_tokens == 100
    assert result.output_tokens == 50
    assert "feature=summarize" in caplog.text
    assert "estimated_cost_usd=" in caplog.text
    assert "test-secret-key" not in caplog.text


def test_groq_does_not_retry_400():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(400, json={"error": "bad request"}, request=request)

    with pytest.raises(AIProviderError) as error:
        _complete(_provider(httpx.MockTransport(handler)))

    assert calls == 1
    assert error.value.provider_status == 400
    assert error.value.retryable is False


def test_groq_retries_5xx():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503, json={"error": "unavailable"}, request=request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"bullets":["One","Two","Three"]}'
                        }
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
            request=request,
        )

    _complete(_provider(httpx.MockTransport(handler)))
    assert calls == 2


def test_groq_timeout_is_retried_once_then_raised():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(AIProviderTimeout):
        _complete(_provider(httpx.MockTransport(handler)))

    assert calls == 2
