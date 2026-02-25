from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from decouple import config
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose.jwt import decode, encode
from passlib.hash import argon2

ALGORITHM = "HS256"
SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return argon2.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return argon2.verify(password, hashed_password)


def encode_access_token(user_id: int) -> dict:
    return {
        "access_token": encode(
            {
                "sub": str(user_id),
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
    }


def decode_access_token(token: str) -> int:
    user_id = decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    return int(user_id)


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

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


auth_dep = Annotated[str, Depends(get_token)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
