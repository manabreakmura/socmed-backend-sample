from typing import List

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlmodel import asc, select

from config.auth import auth_dep, decode_access_token
from config.db import session_dep
from config.log import logger
from users.models import User
from users.schemas import UserRead

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("/")
async def get_users(
    session: session_dep,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> List[UserRead]:
    try:
        statement = select(User).order_by(asc(User.id)).offset(offset).limit(limit)
        results = await session.execute(statement)
        rows = results.scalars().all()
        return rows
    except HTTPException:
        raise
    except Exception as e:
        logger.debug(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_router.delete("/{user_id}")
async def delete_user(session: session_dep, auth: auth_dep, user_id: int) -> Response:
    try:
        if decode_access_token(auth) != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        statement = select(User).where(User.id == user_id)
        results = await session.execute(statement)
        row = results.scalar()

        await session.delete(row)
        await session.commit()

        return Response(status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except Exception as e:
        logger.debug(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
