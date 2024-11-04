from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from config.auth import (
    authenticate,
    create_access_token,
    form_data_dependency,
    get_current_user,
    hash_password,
    token_dependency,
    validate_email,
)
from config.database import session_dependency
from users.models import Token, User

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post("/signup/")
def signup(user: User, session: session_dependency) -> User:
    try:
        user = User(
            username=user.username,
            email=validate_email(user.email),
            password=hash_password(user.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)


@router.get("/users/")
def get_users(session: session_dependency) -> list[User]:
    try:
        statement = select(User)
        return session.exec(statement).all()
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)


@router.post("/auth/token/")
def get_access_token(
    form_data: form_data_dependency, session: session_dependency
) -> Token:
    user = authenticate(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(data={"sub": user.id}),
        "token_type": "bearer",
    }


@router.get("/auth/me/")
def me(session: session_dependency, token: token_dependency) -> User:
    try:
        return get_current_user(session, token)
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)
