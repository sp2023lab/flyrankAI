from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models import User
from app.schemas import ProtectedResponse


router = APIRouter(tags=["protected"])


@router.get("/protected", response_model=ProtectedResponse)
def protected_route(
    current_user: User = Depends(get_current_active_user),
) -> ProtectedResponse:
    return ProtectedResponse(
        message="You are authenticated and may view this protected resource.",
        username=current_user.username,
    )
