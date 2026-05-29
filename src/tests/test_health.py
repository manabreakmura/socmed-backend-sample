import pytest
from fastapi import status

from src.config.settings import settings

pytestmark = pytest.mark.anyio


class TestHealth:
    async def test_pg(self, pg_container):
        assert pg_container.startswith("postgresql+asyncpg://")

    async def test_debug(self, client):
        response = await client.get("/docs")
        if settings.DEBUG:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_cors(self, client):
        for url in settings.origins:
            response = await client.options("/", headers={"Origin": url})
            assert response.headers.get("access-control-allow-origin") == url
