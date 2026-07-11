from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import get_settings
from app.database import ensure_schema
from app.routers import demo, health, reports, summarize

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Path(settings.artifacts_dir).mkdir(parents=True, exist_ok=True)
    ensure_schema()
    yield


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "Generates PDF reports and accepts slow AI summarization work as persistent "
        "Celery background jobs with polling, idempotency, retries, and failure alerts."
    ),
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(demo.router)
app.include_router(reports.router)
app.include_router(summarize.router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": settings.app_name, "docs": "/docs", "health": "/health"}
