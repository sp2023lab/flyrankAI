from functools import lru_cache

from app.ai.base import AIConfigurationError, AIProvider
from app.ai.groq_provider import GroqProvider
from app.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()
    provider_name = settings.ai_provider.strip().lower()

    if provider_name == "groq":
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            timeout_seconds=settings.ai_timeout_seconds,
            max_retries=settings.ai_max_retries,
            retry_backoff_seconds=settings.ai_retry_backoff_seconds,
            input_cost_per_million=settings.groq_input_cost_per_million,
            output_cost_per_million=settings.groq_output_cost_per_million,
        )

    raise AIConfigurationError(f"Unsupported AI provider: {provider_name}")
