from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from decouple import config
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

ALGORITHM = "HS256"
SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
TOKEN_EXPIRE = config("TOKEN_EXPIRE", cast=int)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def hash_password(password):
    return password_context.hash(password)


def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


def create_access_token(user):
    return {
        "access_token": jwt.encode(
            {
                "sub": user.username,
                "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
    }


auth_dep = Annotated[str, Depends(oauth2_scheme)]
oauth2_dep = Annotated[OAuth2PasswordRequestForm, Depends()]
