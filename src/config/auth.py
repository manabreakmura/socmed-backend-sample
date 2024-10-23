from datetime import datetime, timedelta, timezone

import jwt
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import select

from users.models import User

SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def authenticate(session, username: str, password: str):
    statement = select(User).where(User.username == username)
    user = session.execute(statement).scalar_one()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
