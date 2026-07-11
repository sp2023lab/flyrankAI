"""Configuration for the polite scraper."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings, with environment-variable overrides."""

    base_url: str = os.getenv("SCRAPER_BASE_URL", "https://books.toscrape.com/")
    start_url: str = os.getenv("SCRAPER_START_URL", "https://books.toscrape.com/")
    user_agent: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "FlyRankPoliteScraper/1.0 (+mailto:shyampopat2023@gmail.com)",
    )
    request_delay_seconds: float = float(os.getenv("SCRAPER_DELAY_SECONDS", "1.5"))
    timeout_seconds: float = float(os.getenv("SCRAPER_TIMEOUT_SECONDS", "15"))
    max_retries: int = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    output_path: Path = Path(os.getenv("SCRAPER_OUTPUT_PATH", "data/records.jsonl"))


DEFAULT_SETTINGS = Settings()
