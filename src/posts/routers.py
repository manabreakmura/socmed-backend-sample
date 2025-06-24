from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlmodel import desc, select

from config.auth import auth_dep, decode_access_token
from config.db import session_dep
from config.log import logger
from posts.models import Post
from posts.schemas import PostCreate, PostRead, PostUpdate

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.post("/")
async def create_post(
    session: session_dep, auth: auth_dep, data: PostCreate
) -> PostRead:
    try:
        row = Post(title=data.title, body=data.body, user_id=decode_access_token(auth))
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.get("/")
async def get_posts_by_user_id(
    session: session_dep,
    auth: auth_dep,
    user_id: int = Query(ge=1),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[PostRead]:
    try:
        statement = (
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(desc(Post.created_at))
            .offset(offset)
            .limit(limit)
        )
        results = await session.execute(statement)
        rows = results.scalars().all()
        return rows
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.patch("/{post_id}")
async def update_post(
    session: session_dep, auth: auth_dep, post_id: int, data: PostUpdate
) -> PostRead:
    try:
        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if decode_access_token(auth) != row.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(row, key):
                setattr(row, key, value)

        await session.commit()
        await session.refresh(row)

        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@posts_router.delete("/{post_id}")
async def delete_post(session: session_dep, auth: auth_dep, post_id: int) -> Response:
    try:
        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        row = results.scalar()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if decode_access_token(auth) != row.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        await session.delete(row)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
