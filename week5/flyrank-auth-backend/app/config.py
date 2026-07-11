from __future__ import annotations

import os
import secrets
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    secret_key: str
    access_token_expire_minutes: int


def load_settings(database_url: str | None = None) -> Settings:
    """Load runtime settings from environment variables.

    A random development secret is generated when AUTH_SECRET_KEY is absent.
    Set AUTH_SECRET_KEY explicitly in any deployed environment so tokens remain
    valid across process restarts.
    """
    return Settings(
        database_url=database_url
        or os.getenv("DATABASE_URL", "sqlite:///./flyrank_auth.db"),
        secret_key=os.getenv("AUTH_SECRET_KEY") or secrets.token_urlsafe(32),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        ),
    )
