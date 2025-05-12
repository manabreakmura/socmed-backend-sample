from typing import Annotated

from decouple import config
from fastapi import Depends
from redis.asyncio import Redis

client = Redis.from_url(config("CACHE_URL"), decode_responses=True)


async def get_cache():
    async with client as cl:
        try:
            yield cl
        finally:
            await cl.close()


cache_dep = Annotated[Redis, Depends(get_cache)]
