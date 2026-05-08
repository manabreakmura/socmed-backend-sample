import pytest
from fastapi import status

from src.config.settings import settings


@pytest.mark.anyio
async def test_pg(pg_container):
    assert pg_container.get_connection_url().startswith("postgresql+asyncpg://")


@pytest.mark.anyio
async def test_debug(client):
    response = await client.get("/docs")
    if settings.DEBUG:
        assert response.status_code == status.HTTP_200_OK
    else:
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_cors(client):
    for url in settings.origins:
        response = await client.options("/", headers={"Origin": url})
        assert response.headers.get("access-control-allow-origin") == url
