from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import desc, select

from src.config.auth import auth_dep, decode_token
from src.config.cache import cache_dep
from src.config.db import session_dep
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostRead, PostUpdate

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.post("")
async def create_post(
    session: session_dep, token: auth_dep, data: PostCreate
) -> PostRead:
    try:
        payload = decode_token(token, "access_token")
        user_id = payload.get("sub")

        row = Post(body=data.body, user_id=user_id)
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.get("")
async def get_posts(
    session: session_dep,
    _: auth_dep,
    user_id: Optional[int] = Query(None, ge=1),
) -> list[PostRead]:
    try:
        statement = select(Post).order_by(desc(Post.created_at))

        if user_id:
            statement = statement.where(Post.user_id == user_id)

        results = await session.execute(statement)
        rows = results.scalars().all()
        return rows  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.get("/{post_id}")
async def get_post(
    session: session_dep, cache: cache_dep, _: auth_dep, post_id: int
) -> PostRead:
    try:
        cache_key, cache_value = "post", post_id
        cached = await cache.get_(cache_key, cache_value)
        if cached:
            return PostRead.model_validate_json(cached)

        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        cache_obj = PostRead.model_validate(row)
        await cache.set_(cache_key, cache_value, cache_obj.model_dump_json())
        return row  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.patch("/{post_id}")
async def update_post(
    session: session_dep,
    cache: cache_dep,
    token: auth_dep,
    post_id: int,
    data: PostUpdate,
) -> PostRead:
    try:
        cache_key, cache_value = "post", post_id
        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        payload = decode_token(token, "access_token")
        user_id = payload.get("sub")

        if user_id != row.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(row, key):
                setattr(row, key, value)

        await session.commit()
        await session.refresh(row)

        await cache.del_(cache_key, cache_value)

        return row  # type: ignore
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.delete("/{post_id}")
async def delete_post(
    session: session_dep, cache: cache_dep, token: auth_dep, post_id: int
) -> None:
    try:
        cache_key, cache_value = "post", post_id
        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        payload = decode_token(token, "access_token")
        user_id = payload.get("sub")

        if user_id != row.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        await session.delete(row)
        await session.commit()
        await cache.del_(cache_key, cache_value)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
