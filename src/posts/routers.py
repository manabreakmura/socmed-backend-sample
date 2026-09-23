from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import desc, distinct, exists, func, or_, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.posts.models import Bookmark, Comment, Like, Post
from src.posts.schemas import (
    CommentCreate,
    CommentRead,
    PostCreate,
    PostRead,
    PostUpdate,
)
from src.users.models import Follow
from src.users.schemas import UserRead

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.post("", response_model=PostRead)
async def add_post(payload: PostCreate, me: auth_dep, session: session_dep) -> PostRead:
    row = Post(body=payload.body, user_id=me)  # ty: ignore
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=row.user,
        total_likes=0,
        is_liked=False,
        is_bookmarked=False,
    )


@posts_router.get("", response_model=list[PostRead])
async def get_posts(
    me: auth_dep,
    session: session_dep,
    feed: Annotated[bool, Query()] = False,
    user_id: Annotated[UUID | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[PostRead]:
    if feed and user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    statement = (
        select(  # ty: ignore
            Post,
            func.count(distinct(Like.post_id)).label("total_likes"),
            exists()
            .where(Like.user_id == me, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
            exists()
            .where(Bookmark.user_id == me, Bookmark.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_bookmarked"),
            exists()
            .where(Follow.follower_id == me, Follow.following_id == Post.user_id)  # ty: ignore
            .correlate(Post)
            .label("is_following"),
        )
        .outerjoin(Like, Like.post_id == Post.id)
        .outerjoin(Follow, Follow.following_id == Post.user_id)
        .group_by(Post.id)
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )

    if feed:
        statement = statement.where(or_(Follow.follower_id == me, Post.user_id == me))

    if user_id:
        statement = statement.where(Post.user_id == user_id)

    result = await session.execute(statement)
    rows = result.all()

    return [
        PostRead(
            id=row.id,
            body=row.body,
            created_at=row.created_at,
            user=UserRead(
                id=row.user.id,
                username=row.user.username,
                created_at=row.user.created_at,
                is_following=is_following,
            ),
            total_likes=total_likes,
            is_liked=is_liked,
            is_bookmarked=is_bookmarked,
        )
        for row, total_likes, is_liked, is_bookmarked, is_following in rows
    ]


@posts_router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: UUID, me: auth_dep, session: session_dep) -> PostRead:
    statement = (
        select(  # ty: ignore
            Post,
            func.count(distinct(Like.post_id)).label("total_likes"),
            exists()
            .where(Like.user_id == me, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
            exists()
            .where(Bookmark.user_id == me, Bookmark.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_bookmarked"),
            exists()
            .where(Follow.follower_id == me, Follow.following_id == Post.user_id)  # ty: ignore
            .correlate(Post)
            .label("is_following"),
        )
        .outerjoin(Like, Like.post_id == Post.id)
        .outerjoin(Follow, Follow.following_id == Post.user_id)
        .where(Post.id == post_id)
        .group_by(Post.id)
    )

    result = await session.execute(statement)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row, total_likes, is_liked, is_bookmarked, is_following = row

    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=UserRead(
            id=row.user.id,
            username=row.user.username,
            created_at=row.user.created_at,
            is_following=is_following,
        ),
        total_likes=total_likes,
        is_liked=is_liked,
        is_bookmarked=is_bookmarked,
    )


@posts_router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: UUID, payload: PostUpdate, me: auth_dep, session: session_dep
) -> PostRead:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != me:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)

    await session.commit()

    statement = (
        select(  # ty: ignore
            Post,
            func.count(distinct(Like.post_id)).label("total_likes"),
            exists()
            .where(Like.user_id == me, Like.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_liked"),
            exists()
            .where(Bookmark.user_id == me, Bookmark.post_id == Post.id)  # ty: ignore
            .correlate(Post)
            .label("is_bookmarked"),
            exists()
            .where(Follow.follower_id == me, Follow.following_id == Post.user_id)  # ty: ignore
            .correlate(Post)
            .label("is_following"),
        )
        .outerjoin(Like, Like.post_id == Post.id)
        .outerjoin(Follow, Follow.following_id == Post.user_id)
        .where(Post.id == post_id)
        .group_by(Post.id)
    )
    result = await session.execute(statement)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row, total_likes, is_liked, is_bookmarked, is_following = row

    return PostRead(
        id=row.id,
        body=row.body,
        created_at=row.created_at,
        user=UserRead(
            id=row.user.id,
            username=row.user.username,
            created_at=row.user.created_at,
            is_following=is_following,
        ),
        total_likes=total_likes,
        is_liked=is_liked,
        is_bookmarked=is_bookmarked,
    )


@posts_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID, me: auth_dep, session: session_dep) -> None:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != me:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()


@posts_router.post("/{post_id}/comments", response_model=CommentRead)
async def add_comment(
    post_id: UUID, payload: CommentCreate, me: auth_dep, session: session_dep
) -> CommentRead:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row = Comment(body=payload.body, user_id=me, post_id=post_id)  # ty: ignore
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row  # ty: ignore


@posts_router.get("/{post_id}/comments", response_model=list[CommentRead])
async def get_comments(
    post_id: UUID,
    me: auth_dep,
    session: session_dep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[CommentRead]:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(desc(Comment.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(statement)
    rows = result.scalars().all()
    return rows  # ty: ignore


@posts_router.delete(
    "/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    post_id: UUID, comment_id: UUID, me: auth_dep, session: session_dep
) -> None:
    row = await session.get(Comment, comment_id)

    if not row or row.post_id != post_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.user_id != me:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()


@posts_router.post("/{post_id}/like")
async def add_like(
    post_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Like).where(Like.user_id == me, Like.post_id == post_id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        session.add(Like(user_id=me, post_id=post_id))
        await session.commit()

    return {"is_liked": True}


@posts_router.delete("/{post_id}/like")
async def delete_like(
    post_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Like).where(Like.user_id == me, Like.post_id == post_id)
    result = await session.execute(statement)
    row = result.scalar()

    if row:
        await session.delete(row)
        await session.commit()

    return {"is_liked": False}


@posts_router.post("/{post_id}/bookmark")
async def add_bookmark(
    post_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Bookmark).where(
        Bookmark.user_id == me, Bookmark.post_id == post_id
    )
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        session.add(Bookmark(user_id=me, post_id=post_id))
        await session.commit()

    return {"is_bookmarked": True}


@posts_router.delete("/{post_id}/bookmark")
async def delete_bookmark(
    post_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    row = await session.get(Post, post_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Bookmark).where(
        Bookmark.user_id == me, Bookmark.post_id == post_id
    )
    result = await session.execute(statement)
    row = result.scalar()

    if row:
        await session.delete(row)
        await session.commit()

    return {"is_bookmarked": False}
