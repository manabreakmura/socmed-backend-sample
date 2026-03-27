import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_signup_success(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "test@user.com", "username": "testuser", "password": "test"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    for key in ["id", "username"]:
        assert key in data.keys()

    for key in ["email", "hashed_password"]:
        assert key not in data.keys()


@pytest.mark.asyncio
async def test_signup_fail(client, signup_obj):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": signup_obj["email"],
            "username": signup_obj["username"],
            "password": signup_obj["password"],
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_signin_success(client, signup_obj):
    response = await client.post(
        "/api/v1/auth/signin",
        data={
            "username": signup_obj["username"],
            "password": signup_obj["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK

    for cookie in ["access_token", "refresh_token"]:
        assert cookie in client.cookies

    result = response.json()
    assert result.get("access_token")
    assert result.get("refresh_token")


@pytest.mark.asyncio
async def test_signin_fail(client):
    response = await client.post(
        "/api/v1/auth/signin",
        data={
            "username": "err",
            "password": "err",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_signout(authenticated_client):
    await authenticated_client.post("/api/v1/auth/signout")
    for cookie in ["access_token", "refresh_token"]:
        assert cookie not in authenticated_client.cookies

    response_should_fail = await authenticated_client.get("/api/v1/auth/me")
    assert response_should_fail.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh(authenticated_client):
    old_token = authenticated_client.cookies.get("access_token")
    del authenticated_client.cookies["access_token"]

    response = await authenticated_client.post("/api/v1/auth/refresh")
    assert response.status_code == status.HTTP_200_OK

    new_token = authenticated_client.cookies.get("access_token")
    assert old_token != new_token


@pytest.mark.asyncio
async def test_me_success(authenticated_client, signup_obj):
    response = await authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == signup_obj["id"]


@pytest.mark.asyncio
async def test_me_fail(client):
    response_should_fail = await client.get("/api/v1/auth/me")
    assert response_should_fail.status_code == status.HTTP_401_UNAUTHORIZED
