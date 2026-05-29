import pytest
from alembic import command
from alembic.config import Config
from fastapi import status
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
def signup_obj():
    return {
        "email": "test@user.com",
        "username": "testuser",
        "password": "test-user-test-user",
    }


@pytest.fixture
def signin_obj():
    return {
        "username": "testuser",
        "password": "test-user-test-user",
    }


@pytest.fixture
async def post_obj(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/posts", json={"body": "test-post"}
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()


@pytest.fixture
async def comment_obj(authenticated_client, post_obj):
    response = await authenticated_client.post(
        f"/api/v1/posts/{post_obj['id']}/comments",
        json={"body": "test-comment"},
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()


@pytest.fixture
async def client(session):
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as cl:
        app.dependency_overrides[get_session] = lambda: session
        yield cl
        app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(session, signup_obj, signin_obj):
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as cl:
        app.dependency_overrides[get_session] = lambda: session
        await cl.post("/api/v1/auth/signup", json=signup_obj)
        response = await cl.post("/api/v1/auth/signin", data=signin_obj)
        access_token = response.json()["access_token"]
        cl.headers["Authorization"] = f"Bearer {access_token}"
        yield cl
        app.dependency_overrides.clear()
