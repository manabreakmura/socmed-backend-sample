import pytest
from fastapi import status


@pytest.mark.anyio
async def test_create_post_unauthorized_fail(client):
    response = await client.post("/api/v1/posts", json={"body": "test-post"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_create_post_success(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/posts", json={"body": "test-post"}
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["body"] == "test-post"


@pytest.mark.anyio
async def test_create_post_empty_fail(authenticated_client):
    response = await authenticated_client.post("/api/v1/posts", json={"body": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.anyio
async def test_get_all_posts_success(authenticated_client):
    response = await authenticated_client.get("/api/v1/posts")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_all_posts_unauthorized_fail(client):
    response = await client.get("/api/v1/posts")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_post_success(authenticated_client):
    row = (
        await authenticated_client.post("/api/v1/posts", json={"body": "test-post"})
    ).json()

    result = (
        await authenticated_client.patch(
            f"/api/v1/posts/{row['id']}", json={"body": "updated"}
        )
    ).json()
    assert result["body"] == "updated"
    assert result["user"] == row["user"]


@pytest.mark.anyio
async def test_delete_post_success(authenticated_client):
    row = (
        await authenticated_client.post("/api/v1/posts", json={"body": "test-post"})
    ).json()

    response = await authenticated_client.delete(f"/api/v1/posts/{row['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
