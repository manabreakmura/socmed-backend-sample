from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import desc, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostRead, PostUpdate

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.post("", response_model=PostRead)
async def create_post(
    payload: PostCreate, user_id: auth_dep, session: session_dep
) -> PostRead:
    row = Post(body=payload.body, user_id=user_id)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row  # ty: ignore


@posts_router.get("", response_model=list[PostRead])
async def get_posts(
    user_id: auth_dep,
    session: session_dep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostRead]:
    statement = select(Post).order_by(desc(Post.created_at)).offset(offset).limit(limit)
    result = await session.execute(statement)
    rows = result.scalars().all()
    return rows  # ty: ignore


@posts_router.get("/{id}", response_model=PostRead)
async def get_post(id: UUID, user_id: auth_dep, session: session_dep) -> PostRead:
    statement = select(Post).where(Post.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return row  # type: ignore


@posts_router.patch("/{id}", response_model=PostRead)
async def update_post(
    id: UUID, payload: PostUpdate, user_id: auth_dep, session: session_dep
) -> PostRead:
    statement = select(Post).where(Post.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(row, key):
            setattr(row, key, value)

    await session.commit()
    await session.refresh(row)
    return row  # type: ignore


@posts_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: UUID, user_id: auth_dep, session: session_dep) -> None:
    statement = select(Post).where(Post.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()
