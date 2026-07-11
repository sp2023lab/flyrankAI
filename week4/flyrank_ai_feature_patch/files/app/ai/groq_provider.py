import asyncio
import logging
from decimal import Decimal
from typing import Any

import httpx

from app.ai.base import (
    AICompletion,
    AIConfigurationError,
    AIProviderError,
    AIProviderTimeout,
)

logger = logging.getLogger(__name__)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
TOKENS_PER_MILLION = Decimal("1000000")


class GroqProvider:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        timeout_seconds: float,
        max_retries: int,
        retry_backoff_seconds: float,
        input_cost_per_million: float,
        output_cost_per_million: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.input_cost_per_million = Decimal(str(input_cost_per_million))
        self.output_cost_per_million = Decimal(str(output_cost_per_million))
        self.transport = transport

    async def complete(
        self,
        *,
        feature: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
    ) -> AICompletion:
        if not self.api_key:
            raise AIConfigurationError("GROQ_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_completion_tokens": 350,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": f"{feature}_response",
                    "strict": True,
                    "schema": schema,
                },
            },
        }

        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout_seconds),
                    transport=self.transport,
                ) as client:
                    response = await client.post(
                        GROQ_CHAT_COMPLETIONS_URL,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise AIProviderTimeout(
                    "The AI provider timed out.",
                    retryable=True,
                ) from exc
            except httpx.RequestError as exc:
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise AIProviderError(
                    "The AI provider could not be reached.",
                    retryable=True,
                ) from exc

            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise AIProviderError(
                    "The AI provider is temporarily unavailable.",
                    provider_status=response.status_code,
                    retryable=True,
                )

            if response.status_code >= 400:
                raise AIProviderError(
                    "The AI provider rejected the request.",
                    provider_status=response.status_code,
                    retryable=False,
                )

            try:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                input_tokens = int(usage.get("prompt_tokens", 0))
                output_tokens = int(usage.get("completion_tokens", 0))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                if attempt < self.max_retries:
                    await self._backoff(attempt)
                    continue
                raise AIProviderError(
                    "The AI provider returned an invalid response envelope.",
                    retryable=True,
                ) from exc

            estimated_cost = self._estimate_cost(input_tokens, output_tokens)
            logger.info(
                "ai_call feature=%s provider=groq model=%s "
                "input_tokens=%d output_tokens=%d estimated_cost_usd=%.8f",
                feature,
                self.model,
                input_tokens,
                output_tokens,
                float(estimated_cost),
            )
            return AICompletion(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.model,
            )

        raise AIProviderError("The AI provider request failed.", retryable=True)

    async def _backoff(self, attempt: int) -> None:
        delay = self.retry_backoff_seconds * (2**attempt)
        if delay > 0:
            await asyncio.sleep(delay)

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        input_cost = (
            Decimal(input_tokens) / TOKENS_PER_MILLION * self.input_cost_per_million
        )
        output_cost = (
            Decimal(output_tokens) / TOKENS_PER_MILLION * self.output_cost_per_million
        )
        return input_cost + output_cost
