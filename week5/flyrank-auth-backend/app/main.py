from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.config import load_settings
from app.database import Base, create_db_engine, create_session_factory
from app.routers import auth, protected


def create_app(database_url: str | None = None) -> FastAPI:
    settings = load_settings(database_url)
    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="FlyRank Authentication Assignment",
        version="1.0.0",
        description=(
            "Registration, password hashing, JWT login, and a protected route "
            "with explicit 401 and 403 responses."
        ),
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.session_factory = session_factory

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(protected.router)
    return app


app = create_app()
