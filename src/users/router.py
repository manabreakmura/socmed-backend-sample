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
def signup(data: User, session: session_dependency) -> User:
    try:
        user = User(
            username=data.username,
            email=validate_email(data.email),
            password=hash_password(data.password),
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
    return get_current_user(session, token)


@router.patch("/users/{user_id}/")
def update_user(user_id: int, data: User, session: session_dependency) -> User:
    try:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).one()

        if data.username:
            user.username = data.username

        if data.email:
            user.email = validate_email(data.email)

        if data.password:
            user.password = hash_password(data.password)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)


@router.get("/users/{user_id}/")
def get_user(user_id: int, session: session_dependency) -> User:
    try:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).one()
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)


@router.delete("/users/{user_id}/")
def delete_user(user_id: int, session: session_dependency) -> User:
    try:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).one()
        session.delete(user)
        session.commit()
        return user
    except SQLAlchemyError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)
