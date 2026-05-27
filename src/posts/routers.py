from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import desc, exists, func, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.posts.models import Like, Post
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
    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,  # ty: ignore
        like_count=0,
        is_liked=False,
    )


@posts_router.get("", response_model=list[PostRead])
async def get_posts(
    user_id: auth_dep,
    session: session_dep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostRead]:
    statement = (
        select(
            Post,
            func.count(Like.post_id).label("like_count"),  # ty: ignore
            exists()
            .where(Like.user_id == user_id, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
        )
        .outerjoin(Like)
        .group_by(Post.id)  # ty: ignore
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(statement)
    rows = result.all()

    return [
        PostRead(
            id=row.id,
            body=row.body,
            created_at=row.created_at,
            user=row.user,
            like_count=like_count,
            is_liked=is_liked,
        )
        for row, like_count, is_liked in rows
    ]


@posts_router.get("/{id}", response_model=PostRead)
async def get_post(id: UUID, user_id: auth_dep, session: session_dep) -> PostRead:
    statement = (
        select(
            Post,
            func.count(Like.post_id).label("like_count"),  # ty: ignore
            exists()
            .where(Like.user_id == user_id, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
        )
        .outerjoin(Like)
        .where(Post.id == id)
        .group_by(Post.id)  # ty: ignore
    )
    result = await session.execute(statement)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row, like_count, is_liked = row
    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,
        like_count=like_count,
        is_liked=is_liked,
    )


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

    statement = (
        select(
            Post,
            func.count(Like.post_id).label("like_count"),  # ty: ignore
            exists()
            .where(Like.user_id == user_id, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
        )
        .outerjoin(Like)
        .where(Post.id == id)
        .group_by(Post.id)  # ty: ignore
    )
    result = await session.execute(statement)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row, like_count, is_liked = row

    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,
        like_count=like_count,
        is_liked=is_liked,
    )


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


@posts_router.post("/{id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_post(id: UUID, user_id: auth_dep, session: session_dep):
    statement = select(Post).where(Post.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Like).where(Like.user_id == user_id, Like.post_id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if row:
        await session.delete(row)
    else:
        session.add(Like(user_id=user_id, post_id=id))

    await session.commit()
