from decouple import config
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from config.auth import encode_access_token, form_data, hash_password, verify_password
from config.db import session_dep
from config.log import logger
from users.models import User
from users.schemas import UserCreate, UserRead

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
        return row
    except IntegrityError as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post("/login")
async def login(session: session_dep, form_data: form_data, response: Response) -> dict:
    try:
        statement = select(User).where(User.username == form_data.username)
        results = await session.execute(statement)
        row = results.scalar()

        if (not row) or (not verify_password(form_data.password, row.hashed_password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = encode_access_token(row.id)

        response.set_cookie(
            key="access_token",
            value=access_token["access_token"],
            httponly=True,
            max_age=3600,
            samesite="lax",
            secure=False if config("DEBUG", cast=bool) else True,
        )

        return access_token
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
