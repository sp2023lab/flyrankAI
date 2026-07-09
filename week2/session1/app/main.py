from fastapi import FastAPI

from app.routes import router


app = FastAPI(
    title="FlyRank BE-04 API",
    description="FastAPI app using a Postgres repository with Docker Compose.",
    version="1.0.0",
)

app.include_router(router)