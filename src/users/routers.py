from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlmodel import desc, select

from config.auth import auth_dep, decode_access_token
from config.cache import cache_dep
from config.db import session_dep
from config.log import logger
from users.models import User
from users.schemas import UserRead

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("/")
async def get_users(
    session: session_dep,
    auth: auth_dep,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[UserRead]:
    try:
        statement = (
            select(User).order_by(desc(User.created_at)).offset(offset).limit(limit)
        )
        results = await session.execute(statement)
        rows = results.scalars().all()
        return rows
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_router.get("/{user_id}")
async def get_user_by_id(
    session: session_dep, auth: auth_dep, cache: cache_dep, user_id: int
) -> UserRead:
    CACHE_KEY = f"user:{user_id}"
    try:
        if await cache.exists(CACHE_KEY):
            return await cache._get(CACHE_KEY)

        statement = select(User).where(User.id == user_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        cache_data = UserRead.model_validate(row)
        await cache._set(CACHE_KEY, cache_data)

        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_router.delete("/{user_id}")
async def delete_user(
    session: session_dep, cache: cache_dep, auth: auth_dep, user_id: int
) -> Response:
    CACHE_KEY = f"user:{user_id}"
    try:
        statement = select(User).where(User.id == user_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if decode_access_token(auth) != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        await session.delete(row)
        await session.commit()

        await cache._del(CACHE_KEY)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
