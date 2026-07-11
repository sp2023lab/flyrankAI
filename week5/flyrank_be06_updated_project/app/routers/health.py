from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health", response_model=HealthResponse)
def health(db: DbSession) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", database="ok")
