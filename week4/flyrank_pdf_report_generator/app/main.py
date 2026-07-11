from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import get_settings
from app.database import ensure_schema
from app.routers import demo, health, reports

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.artifacts_dir).mkdir(parents=True, exist_ok=True)
    ensure_schema()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Queries order data, aggregates it with SQL, generates PDF artifacts in a Celery "
        "background worker, and exposes job-status and download endpoints."
    ),
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(demo.router)
app.include_router(reports.router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }
