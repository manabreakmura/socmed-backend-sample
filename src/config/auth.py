from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Optional
from uuid import uuid4

from argon2 import PasswordHasher
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jwt import PyJWTError, decode, encode

from src.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

ph = PasswordHasher()

ACCESS_TOKEN_EXPIRE_COOKIE = settings.ACCESS_TOKEN_EXPIRE * 60
REFRESH_TOKEN_EXPIRE_COOKIE = settings.REFRESH_TOKEN_EXPIRE * 24 * 60 * 60
SECURE_COOKIE = False if settings.DEBUG else True


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except Exception:
        return False


def encode_token(
    user_id: int | str, expected_type: Literal["access_token", "refresh_token"]
) -> str:
    try:
        now = datetime.now(timezone.utc)
        delta = (
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
            if expected_type == "access_token"
            else timedelta(days=settings.REFRESH_TOKEN_EXPIRE)
        )

        return encode(
            {
                "sub": str(user_id),
                "type": expected_type,
                "exp": now + delta,
                "jti": str(uuid4()),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


def decode_token(
    data: str, expected_type: Literal["access_token", "refresh_token"]
) -> dict[str, str | int | None]:
    try:
        payload = decode(data, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if not payload.get("type") == expected_type:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return {
            "sub": int(sub),
            "type": payload.get("type"),
            "exp": payload.get("exp"),
        }
    except PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_token(
    request: Request,
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> str:
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    if oauth2_token:
        return oauth2_token

    if bearer:
        return bearer.credentials

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


def set_auth_cookie(
    response: Response, key: Literal["access_token", "refresh_token"], value: str
) -> None:
    max_age = (
        ACCESS_TOKEN_EXPIRE_COOKIE
        if key == "access_token"
        else REFRESH_TOKEN_EXPIRE_COOKIE
    )
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        secure=SECURE_COOKIE,
        httponly=True,
        samesite="lax",
    )


def delete_auth_cookie(
    response: Response, key: Literal["access_token", "refresh_token"]
) -> None:
    response.delete_cookie(key=key, secure=SECURE_COOKIE)


auth_dep = Annotated[str, Depends(get_token)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
