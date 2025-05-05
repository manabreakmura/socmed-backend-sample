from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config.auth import (
    auth_dep,
    encode_token,
    hash_password,
    oauth2_dep,
    verify_password,
)
from config.db import session_dep
from users.models import User
from users.schemas import UserRequestSchema, UserResponseSchema

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@auth_router.post("/signup")
async def signup(data: UserRequestSchema, session: session_dep) -> UserResponseSchema:
    try:
        user = User(
            email=data.email,
            username=data.username,
            password=hash_password(data.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user, attribute_names=["posts"])
        return user
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )


@auth_router.post("/login")
async def login(session: session_dep, form_data: oauth2_dep) -> dict:
    statement = select(User).filter(User.username == form_data.username)
    results = await session.execute(statement)
    user = results.scalar_one_or_none()

    if (not user) or (not verify_password(form_data.password, user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return encode_token(user)


@users_router.get("/")
async def get_users(session: session_dep, auth: auth_dep) -> List[UserResponseSchema]:
    try:
        statement = (
            select(User).options(selectinload(User.posts)).order_by("created_at")
        )
        results = await session.execute(statement)
        return results.scalars()
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )
