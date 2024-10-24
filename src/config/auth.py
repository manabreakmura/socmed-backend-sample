from datetime import datetime, timedelta, timezone

import jwt
from decouple import config
from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from users.models import User

SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate(session, username: str, password: str):
    try:
        statement = select(User).where(User.username == username)
        user = session.execute(statement).scalar_one()
    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exception)
        )

    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(session, token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.id == user_id)
    user = session.execute(statement).scalar_one()
    if user is None:
        raise credentials_exception
    return user


def validate_email_or_raise(email):
    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )
