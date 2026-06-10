from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import desc, exists, func, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.posts.models import Comment, Like, Post
from src.posts.schemas import (
    CommentCreate,
    CommentRead,
    PostCreate,
    PostRead,
    PostUpdate,
)
from src.users.models import Follow

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
        total_likes=0,
        is_liked=False,
    )


@posts_router.get("", response_model=list[PostRead])
async def get_posts(
    user_id: auth_dep,
    session: session_dep,
    id: UUID = Query(default=None),  # noqa
    feed: bool = Query(default=False),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostRead]:

    if id and feed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    statement = select(
        Post,
        func.count(Like.post_id).label("total_likes"),  # ty: ignore
        exists()
        .where(Like.user_id == user_id, Like.post_id == Post.id)  # ty: ignore
        .correlate(Post)
        .label("is_liked"),
    )
    if id:
        statement = statement.where(Post.user_id == id)

    if feed:
        statement = statement.join(Follow, Post.user_id == Follow.following_id).where(  # ty: ignore
            Follow.follower_id == user_id
        )

    statement = (
        statement.outerjoin(Like)
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
            total_likes=total_likes,
            is_liked=is_liked,
        )
        for row, total_likes, is_liked in rows
    ]


@posts_router.get("/{id}", response_model=PostRead)
async def get_post(id: UUID, user_id: auth_dep, session: session_dep) -> PostRead:
    statement = (
        select(
            Post,
            func.count(Like.post_id).label("total_likes"),  # ty: ignore
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

    row, total_likes, is_liked = row
    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,
        total_likes=total_likes,
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
            func.count(Like.post_id).label("total_likes"),  # ty: ignore
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

    row, total_likes, is_liked = row

    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,
        total_likes=total_likes,
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


@posts_router.post("/{id}/like")
async def like(id: UUID, user_id: auth_dep, session: session_dep) -> dict[str, bool]:
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
        is_liked = False
    else:
        session.add(Like(user_id=user_id, post_id=id))
        is_liked = True

    await session.commit()
    return {"is_liked": is_liked}


@posts_router.post("/{id}/comments", response_model=CommentRead)
async def create_comment(
    id: UUID, payload: CommentCreate, user_id: auth_dep, session: session_dep
) -> CommentRead:
    statement = select(Post).where(Post.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row = Comment(body=payload.body, user_id=user_id, post_id=id)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row  # ty: ignore


@posts_router.get("/{id}/comments", response_model=list[CommentRead])
async def get_comments(
    id: UUID, user_id: auth_dep, session: session_dep
) -> list[CommentRead]:
    statement = (
        select(Comment).where(Comment.post_id == id).order_by(desc(Comment.created_at))
    )
    result = await session.execute(statement)
    rows = result.scalars().all()
    return rows  # ty: ignore


@posts_router.delete(
    "/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    post_id: UUID, comment_id: UUID, user_id: auth_dep, session: session_dep
) -> None:
    statement = select(Comment).where(Comment.id == comment_id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row or row.post_id != post_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()
