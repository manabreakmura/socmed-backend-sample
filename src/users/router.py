from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from config.auth import hash_password, validate_email
from config.database import session_dependency
from users.models import User

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
