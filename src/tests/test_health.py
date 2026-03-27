import pytest

from src.config.settings import settings


@pytest.mark.asyncio
async def test_startup(client):
    response = await client.get("/")
    assert hasattr(response, "status_code")


@pytest.mark.asyncio
async def test_cors(client):
    for URL in settings.FRONTEND_URL.split(","):
        response = await client.options("/docs", headers={"Origin": URL})
        assert response.headers.get("access-control-allow-origin") == URL


@pytest.mark.asyncio
async def test_debug(client):
    response = await client.get("/docs")
    if settings.DEBUG:
        assert response.status_code == 200
