from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from config.auth import auth_dep, decode_token
from config.db import session_dep
from posts.models import Post
from posts.schemas import PostRequestSchema, PostResponseSchema

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.get("/")
async def get_posts(session: session_dep) -> List[PostResponseSchema]:
    try:
        statement = select(Post).order_by("created_at")
        results = await session.execute(statement)
        return results.scalars()
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )


@posts_router.post("/")
async def create_post(
    data: PostRequestSchema, session: session_dep, auth: auth_dep
) -> PostResponseSchema:
    post = Post(title=data.title, body=data.body, user_id=decode_token(auth))
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
