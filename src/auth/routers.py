from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.orm import load_only
from sqlmodel import or_, select

from src.config.auth import auth_dep, form_data, pa, to
from src.config.db import session_dep
from src.users.models import User
from src.users.schemas import UserCreate, UserRead

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/signup", response_model=UserRead)
async def signup(payload: UserCreate, session: session_dep) -> UserRead:
    statement = select(
        select(User)
        .where(
            or_(
                User.email == payload.email,
                User.username == payload.username,
            )
        )
        .exists()
    )
    result = await session.execute(statement)
    if result.scalar():
        raise HTTPException(status.HTTP_409_CONFLICT)

    row = User(
        email=payload.email,
        username=payload.username,
        hashed_password=pa.hash_password(payload.password.get_secret_value()),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row  # ty: ignore


@auth_router.post("/signin")
async def signin(
    payload: form_data, session: session_dep, response: Response
) -> dict[str, str]:
    statement = (
        select(User)
        .where(User.username == payload.username)
        .options(load_only(User.id, User.hashed_password))  # ty: ignore
    )
    result = await session.execute(statement)
    row = result.scalar()
    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if not pa.verify_password(row.hashed_password, payload.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    access_token = to.encode_token(row.id, "access_token")
    refresh_token = to.encode_token(row.id, "refresh_token")

    to.set_cookie(response, "access_token", access_token)
    to.set_cookie(response, "refresh_token", refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_router.post("/signout")
async def signout(user_id: auth_dep, response: Response) -> None:
    to.delete_cookie(response, "access_token")
    to.delete_cookie(response, "refresh_token")


@auth_router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user_id = to.decode_token(refresh_token, "refresh_token")["sub"]
    access_token = to.encode_token(user_id, "access_token")
    to.set_cookie(response, "access_token", access_token)
    return {"access_token": access_token}


@auth_router.get("/me")
async def me(user_id: auth_dep, session: session_dep) -> UserRead:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    row = result.scalar()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return row  # ty: ignore
