from datetime import datetime, timedelta, timezone
from os import environ

import jwt
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import select

from users.models import User

load_dotenv()

SECRET_KEY = environ["SECRET_KEY"]  # openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES = environ["ACCESS_TOKEN_EXPIRE_MINUTES"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def authenticate(session, username: str, password: str):
    statement = select(User).where(User.username == username)
    user = session.execute(statement).scalar_one()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
