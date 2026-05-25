import pytest
from fastapi import status


@pytest.mark.anyio
async def test_signup_duplicate(authenticated_client, signup_obj):
    response = await authenticated_client.post("/api/v1/auth/signup", json=signup_obj)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_signup_weak_password(client, signup_obj):
    response = await client.post(
        "/api/v1/auth/signup", json={**signup_obj, "password": "weak_password"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.anyio
async def test_signin_success(client, signin_obj):
    response = await client.post("/api/v1/auth/signin", data=signin_obj)
    assert response.status_code == status.HTTP_200_OK

    for cookie in ["access_token", "refresh_token"]:
        assert cookie in client.cookies


@pytest.mark.anyio
async def test_signin_wrong_password(client):
    response = await client.post(
        "/api/v1/auth/signin",
        data={"username": "testuser", "password": "wrong-password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_me_success(authenticated_client):
    response = await authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    for key in ["id", "email", "username", "created_at"]:
        assert key in result.keys()

    for item in ["test@user.com", "testuser"]:
        assert item in result.values()
