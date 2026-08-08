from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/widget_platform"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
    max_submission_body_bytes: int = int(os.getenv("MAX_SUBMISSION_BODY_BYTES", "16384"))
    rate_limit_ip_per_minute: int = int(os.getenv("RATE_LIMIT_IP_PER_MINUTE", "5"))
    rate_limit_widget_per_minute: int = int(os.getenv("RATE_LIMIT_WIDGET_PER_MINUTE", "100"))
    trust_proxy: bool = _bool("TRUST_PROXY", False)
    ip_hash_salt: str = os.getenv("IP_HASH_SALT", "development-only-change-me")
    geo_provider_a_enabled: bool = _bool("GEO_PROVIDER_A_ENABLED", True)
    geo_provider_b_enabled: bool = _bool("GEO_PROVIDER_B_ENABLED", True)
    geo_request_timeout_seconds: float = float(os.getenv("GEO_REQUEST_TIMEOUT_SECONDS", "1.5"))
    notification_max_attempts: int = int(os.getenv("NOTIFICATION_MAX_ATTEMPTS", "3"))
    notification_poll_interval_seconds: float = float(os.getenv("NOTIFICATION_POLL_INTERVAL_SECONDS", "2"))
    notification_force_fail: bool = _bool("NOTIFICATION_FORCE_FAIL", False)


@lru_cache

def get_settings() -> Settings:
    return Settings()
