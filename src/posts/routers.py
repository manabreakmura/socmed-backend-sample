import json
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import desc, select

from config.auth import auth_dep, decode_token
from config.cache import cache_dep
from config.db import session_dep
from posts.models import Post
from posts.schemas import PostRequestSchema, PostResponseSchema

posts_router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@posts_router.get("/")
async def get_posts(session: session_dep, cache: cache_dep) -> List[PostResponseSchema]:
    try:
        if await cache.exists("posts"):
            results = await cache.get("posts")
            return [
                PostResponseSchema.model_validate_json(x) for x in json.loads(results)
            ]
        else:
            statement = select(Post).order_by(desc("created_at"))
            results = await session.execute(statement)
            results = results.scalars()
            results = [PostResponseSchema.model_validate(x) for x in results]

            await cache.set("posts", json.dumps([x.model_dump_json() for x in results]))
            return results
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )


@posts_router.get("/{post_id}")
async def get_post_by_id(session: session_dep, post_id: int) -> PostResponseSchema:
    try:
        statement = select(Post).where(Post.id == post_id)
        results = await session.execute(statement)
        return results.scalar_one()
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )


@posts_router.post("/")
async def create_post(
    data: PostRequestSchema, session: session_dep, auth: auth_dep, cache: cache_dep
) -> PostResponseSchema:
    try:
        results = Post(title=data.title, body=data.body, user_id=decode_token(auth))
        session.add(results)
        await session.commit()
        await session.refresh(results)

        if await cache.exists("posts"):
            await cache.delete("posts")
        return results
    except Exception as exception:
        raise HTTPException(
            detail=exception.args, status_code=status.HTTP_400_BAD_REQUEST
        )
