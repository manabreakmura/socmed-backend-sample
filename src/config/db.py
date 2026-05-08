from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session() as se:
        yield se


session_dep = Annotated[AsyncSession, Depends(get_session)]
