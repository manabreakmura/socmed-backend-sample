from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends
from redis.asyncio import Redis

from src.config.settings import settings


class RedisClient(Redis):  # type: ignore
    async def get_(self, key: str, value: int) -> Optional[str]:
        return await super().get(f"{key}:{value}")

    async def set_(self, key: str, value: int, obj: str, ttl: int = 600) -> None:
        await super().set(f"{key}:{value}", obj, ex=ttl)

    async def del_(self, key: str, value: int) -> None:
        await super().delete(f"{key}:{value}")


cache = RedisClient.from_url(settings.CACHE_URL, decode_responses=True)


async def get_cache() -> AsyncGenerator[RedisClient, None]:
    yield cache  # type: ignore


cache_dep = Annotated[RedisClient, Depends(get_cache)]
