import pytest
from fastapi import status


@pytest.mark.anyio
async def test_signup_success(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@user.com",
            "username": "testuser",
            "password": "test-user-test-user",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    for key in ["id", "email", "username", "created_at"]:
        assert key in data.keys()

    for key in ["hashed_password"]:
        assert key not in data.keys()


@pytest.mark.anyio
async def test_signup_duplicate(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@user.com",
            "username": "testuser",
            "password": "test-user-test-user",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_signup_weak_password(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@user.com",
            "username": "testuser",
            "password": "weak_password",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.anyio
async def test_signin_success(client):
    response = await client.post(
        "/api/v1/auth/signin",
        data={"username": "testuser", "password": "test-user-test-user"},
    )
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
async def test_me_success(client):
    token = await client.post(
        "/api/v1/auth/signin",
        data={"username": "testuser", "password": "test-user-test-user"},
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token.json()['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    for key in ["id", "email", "username", "created_at"]:
        assert key in result.keys()

    for item in ["test@user.com", "testuser"]:
        assert item in result.values()
