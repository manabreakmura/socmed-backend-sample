from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from decouple import config
from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_email
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from users.models import User

SECRET_KEY = config("SECRET_KEY")  # openssl rand -hex 32
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token/")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def validate_email(email):
    try:
        return _validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate(session, username: str, password: str):
    try:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).one()

        if verify_password(password, user.password):
            return user
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_404_NOT_FOUND, exception.args)


def jwt_decode(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(session, token):
    payload = jwt_decode(token)
    try:
        statement = select(User).where(User.id == payload.get("sub"))
        return session.exec(statement).one()
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_404_NOT_FOUND, exception.args)


form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
token_dependency = Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]
