import pytest
from fastapi import status

from src.config.settings import settings


@pytest.mark.asyncio
async def test_startup(client):
    response = await client.get("/")
    assert hasattr(response, "status_code")


@pytest.mark.asyncio
async def test_cors(client):
    for url in settings.origins:
        response = await client.options("/docs", headers={"Origin": url})
        assert response.headers.get("access-control-allow-origin") == url


@pytest.mark.asyncio
async def test_debug(client):
    response = await client.get("/docs")
    if settings.DEBUG:
        assert response.status_code == status.HTTP_200_OK
