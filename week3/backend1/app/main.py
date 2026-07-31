from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import router


app = FastAPI(
    title="FlyRank Week 3 - SQLite CRUD API",
    description="FastAPI task CRUD API backed by SQLite persistence.",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": detail},
        headers=exc.headers,
    )


app.include_router(router)