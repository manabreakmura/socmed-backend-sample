from typing import Annotated

from decouple import config
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

engine = create_async_engine(config("DATABASE_URL"), echo=True)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session() as se:
        yield se


async def create_db_tables():
    from users.models import User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


session_dep = Annotated[AsyncSession, Depends(get_session)]
