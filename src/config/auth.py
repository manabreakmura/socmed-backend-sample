from datetime import datetime, timedelta, timezone
from typing import Annotated

from decouple import config
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose.jwt import decode, encode
from passlib.hash import bcrypt

ALGORITHM = "HS256"
SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.verify(password, hashed_password)


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


auth_dep = Annotated[str, Depends(oauth2_scheme)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
