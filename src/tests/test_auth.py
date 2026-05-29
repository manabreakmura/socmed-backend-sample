import pytest
from fastapi import status

pytestmark = pytest.mark.anyio


class TestAuth:
    async def test_signup_duplicate(self, authenticated_client, signup_obj):
        assert (
            await authenticated_client.post("/api/v1/auth/signup", json=signup_obj)
        ).status_code == status.HTTP_409_CONFLICT

    async def test_signup_weak_password(self, client, signup_obj):
        assert (
            await client.post(
                "/api/v1/auth/signup", json={**signup_obj, "password": "weak-password"}
            )
        ).status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_signin_success(self, client, signin_obj):
        response = await client.post("/api/v1/auth/signin", data=signin_obj)
        assert response.status_code == status.HTTP_200_OK

        for cookie in ["access_token", "refresh_token"]:
            assert cookie in client.cookies

    async def test_signin_wrong_password(self, client):
        assert (
            await client.post(
                "/api/v1/auth/signin",
                data={"username": "testuser", "password": "wrong-password"},
            )
        ).status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_success(self, authenticated_client):
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_200_OK

        result = response.json()

        for key in ["id", "email", "username", "created_at"]:
            assert key in result
