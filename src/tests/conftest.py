import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.config.db import get_session
from src.main import app
from src.users.models import User  # noqa


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as se:
        yield se

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(session):
    app.dependency_overrides[get_session] = lambda: session

    try:
        async with AsyncClient(
            transport=ASGITransport(app), base_url="http://test"
        ) as cl:
            yield cl
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def signup_obj(client):
    data = {"email": "test@user.com", "username": "testuser", "password": "test"}
    response = await client.post("/api/v1/auth/signup", json=data)
    assert response.status_code == 200
    user = response.json()
    user["email"] = data["email"]
    user["password"] = data["password"]
    return user


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client, signup_obj):
    response = await client.post(
        "/api/v1/auth/signin",
        data={
            "username": signup_obj["username"],
            "password": signup_obj["password"],
        },
    )
    assert response.status_code == 200
    return client
