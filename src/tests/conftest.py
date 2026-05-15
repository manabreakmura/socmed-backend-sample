import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.config.db import get_session
from src.config.settings import settings
from src.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer(image="postgres:18.3-alpine3.23", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest.fixture(scope="session")
def migrations(pg_container):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(settings, "DATABASE_URL", pg_container)
        alembic = Config("alembic.ini")
        command.upgrade(alembic, "head")
        yield


@pytest.fixture(scope="session")
async def engine(migrations):
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def session(engine):
    async with async_sessionmaker(engine, expire_on_commit=False)() as se:
        yield se


@pytest.fixture
async def client(session):
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as cl:
        app.dependency_overrides[get_session] = lambda: session
        yield cl
        app.dependency_overrides.clear()
