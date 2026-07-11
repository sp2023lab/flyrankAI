from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies import credentials_exception, get_current_active_user
from app.models import User
from app.schemas import AccountStatusResponse, Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
) -> User:
    existing_user = session.scalar(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        )

    user = User(
        username=payload.username,
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    # The OAuth2 field is named "username", but this service accepts either
    # a username or an email address for convenience.
    identifier = form_data.username
    user = session.scalar(
        select(User).where(
            or_(User.username == identifier, User.email == identifier.lower())
        )
    )

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception()
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    settings = request.app.state.settings
    token = create_access_token(
        subject=user.username,
        secret_key=settings.secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )
    return Token(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return current_user


@router.post("/deactivate", response_model=AccountStatusResponse)
def deactivate_current_user(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> AccountStatusResponse:
    current_user.is_active = False
    session.add(current_user)
    session.commit()
    return AccountStatusResponse(
        message="Account deactivated",
        is_active=False,
    )
