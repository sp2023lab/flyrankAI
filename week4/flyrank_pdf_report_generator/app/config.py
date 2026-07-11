from functools import lru_cache
from pathlib import Path

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
