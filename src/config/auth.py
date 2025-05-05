from datetime import datetime, timedelta, timezone
from typing import Annotated

from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

ALGORITHM = "HS256"
SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
TOKEN_EXPIRE = config("TOKEN_EXPIRE", cast=int)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def hash_password(password: str):
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)


def encode_token(user) -> dict:
    return {
        "access_token": encode(
            {
                "sub": str(user.id),
                "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
    }


def decode_token(token: str) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except InvalidTokenError:
        raise credentials_exception


auth_dep = Annotated[str, Depends(oauth2_scheme)]
oauth2_dep = Annotated[OAuth2PasswordRequestForm, Depends()]
