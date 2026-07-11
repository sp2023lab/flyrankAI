from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AICompletion:
    content: str
    input_tokens: int
    output_tokens: int
    model: str


class AIProvider(Protocol):
    async def complete(
        self,
        *,
        feature: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
    ) -> AICompletion: ...


class AIConfigurationError(RuntimeError):
    """Raised when the selected AI provider is not configured correctly."""


class AIProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        provider_status: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.provider_status = provider_status
        self.retryable = retryable


class AIProviderTimeout(AIProviderError):
    """Raised when all timeout attempts have been exhausted."""
