from fastapi import APIRouter, HTTPException, status
from sqlmodel import desc, select

from src.config.auth import auth_dep
from src.config.cache import cache_dep
from src.config.db import session_dep
from src.users.models import User
from src.users.schemas import UserRead

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("")
async def get_users(session: session_dep, _: auth_dep) -> list[UserRead]:
    try:
        statement = select(User).order_by(desc(User.created_at))
        results = await session.execute(statement)
        rows = results.scalars().all()
        return rows  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_router.get("/{user_id}")
async def get_user(
    session: session_dep, cache: cache_dep, _: auth_dep, user_id: int
) -> UserRead:
    try:
        cache_key, cache_value = "user", user_id
        cached = await cache.get_(cache_key, cache_value)
        if cached:
            return UserRead.model_validate_json(cached)

        statement = select(User).where(User.id == user_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        cache_obj = UserRead.model_validate(row)
        await cache.set_(cache_key, cache_value, cache_obj.model_dump_json())
        return row  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
