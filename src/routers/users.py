from email_validator import validate_email
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from config.auth import auth_dependency, get_password_hash
from config.database import session_dependency
from models.users import User

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.post("/")
async def create_user(session: session_dependency, data: User):
    try:
        user = User(
            username=data.username,
            email=validate_email(data.email, check_deliverability=False).normalized,
            password=get_password_hash(data.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )


@users_router.get("/")
async def get_users(session: session_dependency, auth: auth_dependency):
    try:
        statement = select(User).order_by("created_at")
        return session.exec(statement).all()
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )
