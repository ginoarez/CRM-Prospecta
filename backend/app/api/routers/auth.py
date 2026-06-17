from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core import security
from app.core.database import get_db
from app.models import User
from app.schemas.auth import (
    AccessTokenOut, LoginIn, RefreshIn, RegisterIn, TokenOut, UserOut,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    try:
        return auth_service.register_user(db, body.email, body.password, body.full_name)
    except auth_service.AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate(db, body.email, body.password)
    except auth_service.AuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return TokenOut(
        access_token=security.create_access_token(str(user.id)),
        refresh_token=security.create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=AccessTokenOut)
def refresh(body: RefreshIn):
    try:
        payload = security.decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise JWTError("not a refresh token")
        sub = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
    return AccessTokenOut(access_token=security.create_access_token(sub))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
