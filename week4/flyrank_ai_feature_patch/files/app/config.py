from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FlyRank PDF Report Generator"
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///./report_generator.db"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    artifacts_dir: Path = Path("./artifacts")
    enable_scheduled_reports: bool = False
    schedule_hour_utc: int = 8
    schedule_minute_utc: int = 0

    ai_provider: str = "groq"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"
    ai_timeout_seconds: float = Field(default=20.0, gt=0, le=120)
    ai_max_retries: int = Field(default=1, ge=0, le=5)
    ai_retry_backoff_seconds: float = Field(default=0.5, ge=0, le=30)
    groq_input_cost_per_million: float = Field(default=0.075, ge=0)
    groq_output_cost_per_million: float = Field(default=0.30, ge=0)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
