import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from src.main import app


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer(image="postgres:18.3-alpine3.23", driver="asyncpg") as pg:
        yield pg


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as cl:
        yield cl
