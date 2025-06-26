from typing import Annotated

from decouple import config
from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel import SQLModel

from config.log import logger


class RedisClient(Redis):
    async def _set(self, cache_key: str, obj: SQLModel):
        await self.hset(name=cache_key, mapping=obj.model_dump(mode="json"))
        await self.expire(cache_key, 3600)
        logger.debug(f"CACHE: SET {cache_key}")

    async def _get(self, cache_key: str):
        results = await self.hgetall(cache_key)
        logger.debug(f"CACHE: GET {cache_key}")
        return results

    async def _del(self, cache_key: str):
        await self.delete(cache_key)
        logger.debug(f"CACHE: DEL {cache_key}")


cache = RedisClient.from_url(config("CACHE_URL"), decode_responses=True)


async def get_cache():
    async with cache as ca:
        yield ca


cache_dep = Annotated[Redis, Depends(get_cache)]
