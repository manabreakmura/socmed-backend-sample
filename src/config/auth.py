from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID, uuid7

from argon2 import PasswordHasher
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import decode, encode

from src.config.settings import settings


class Password(PasswordHasher):
    def hash_password(self, password: str) -> str:
        return self.hash(password)

    def verify_password(self, hashed_password: str, password: str) -> bool:
        try:
            return self.verify(hashed_password, password)
        except Exception:
            return False


class Token:
    expected_type = Literal["access_token", "refresh_token"]
    bearer_token = Annotated[
        str | None,
        Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin", auto_error=False)),
    ]

    def encode_token(self, user_id, expected_type: expected_type) -> str:
        now = datetime.now(UTC)
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
                "jti": str(uuid7()),
            },
            settings.SECRET_KEY.get_secret_value(),
            settings.ALGORITHM,
        )

    def decode_token(self, payload: str, expected_type: expected_type):
        result = decode(
            payload,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=settings.ALGORITHM,
        )

        if not result.get("sub"):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if expected_type != result.get("type"):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return {
            "sub": result.get("sub"),
            "type": result.get("type"),
            "exp": result.get("exp"),
            "jti": result.get("jti"),
        }

    def set_cookie(self, response: Response, cookie: expected_type, value: str) -> None:
        max_age = (
            (settings.ACCESS_TOKEN_EXPIRE * 60)
            if cookie == "access_token"
            else (settings.REFRESH_TOKEN_EXPIRE * 24 * 60 * 60)
        )
        response.set_cookie(
            key=cookie,
            value=value,
            max_age=max_age,
            secure=True,
            httponly=True,
            samesite="lax",
        )

    def delete_cookie(self, response: Response, cookie: expected_type) -> None:
        response.delete_cookie(key=cookie, secure=True)

    def authenticate(self, request: Request, bearer_token: bearer_token) -> UUID:
        token = request.cookies.get("access_token") or bearer_token

        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return UUID(self.decode_token(token, "access_token")["sub"])


pa = Password()
to = Token()

form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
auth_dep = Annotated[UUID, Depends(to.authenticate)]
