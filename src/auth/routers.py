from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.config.auth import (
    auth_dep,
    decode_token,
    delete_auth_cookie,
    encode_token,
    form_data,
    hash_password,
    set_auth_cookie,
    verify_password,
)
from src.config.db import session_dep
from src.users.models import User
from src.users.schemas import UserCreate, UserRead

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/signup")
async def signup(session: session_dep, data: UserCreate) -> UserRead:
    try:
        row = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row  # type: ignore
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post("/signin")
async def signin(
    session: session_dep, form_data: form_data, response: Response
) -> dict[str, str]:
    try:
        statement = select(User).where(User.username == form_data.username)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if not verify_password(row.hashed_password, form_data.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        access_token = encode_token(row.id, "access_token")
        refresh_token = encode_token(row.id, "refresh_token")

        set_auth_cookie(response, "access_token", access_token)
        set_auth_cookie(response, "refresh_token", refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post("/signout")
async def signout(response: Response) -> None:
    try:
        delete_auth_cookie(response, "access_token")
        delete_auth_cookie(response, "refresh_token")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.get("/me")
async def me(session: session_dep, token: auth_dep) -> UserRead:
    try:
        payload = decode_token(token, "access_token")
        user_id = payload.get("sub")

        statement = select(User).where(User.id == user_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        return row  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post("/refresh")
async def refresh(response: Response, request: Request) -> None:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        payload = decode_token(refresh_token, "refresh_token")
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        access_token = encode_token(sub, "access_token")
        set_auth_cookie(response, "access_token", access_token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
