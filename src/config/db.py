from typing import Annotated

from decouple import config
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(config("DATABASE_URL"), echo=True)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session as se:
        yield se


session_dependency = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass
