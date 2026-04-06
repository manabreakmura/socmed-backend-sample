import pytest
from fastapi import status

from src.posts.schemas import PostRead
from src.posts.types import POST_BODY_MAX_LEN


@pytest.mark.asyncio
async def test_create_post_guest(client):
    response = await client.post("/api/v1/posts", json={"body": "post"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            {"body": "a" * (POST_BODY_MAX_LEN + 1)},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ),
        ({"body": "a" * (POST_BODY_MAX_LEN)}, status.HTTP_200_OK),
        ({"body": ""}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
async def test_create_post(authenticated_client, payload, expected_status):
    response = await authenticated_client.post("/api/v1/posts", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_posts(authenticated_client, post_factory):
    posts = []
    for obj in ["post", "post"]:
        posts.append(await post_factory(obj))

    response = await authenticated_client.get("/api/v1/posts")
    assert response.status_code == status.HTTP_200_OK

    results = response.json()
    assert len(results) == len(posts)
    for obj in results:
        assert isinstance(obj["id"], int)
        assert isinstance(obj["user"]["username"], str)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "post_id, expected_status",
    [
        (1, status.HTTP_200_OK),
        (999, status.HTTP_404_NOT_FOUND),
    ],
)
async def test_get_post(authenticated_client, post_factory, post_id, expected_status):
    obj = await post_factory("post")
    response = await authenticated_client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        assert (
            PostRead.model_validate(response.json()).model_dump()
            == PostRead.model_validate(obj).model_dump()
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (
            {"body": "a" * (POST_BODY_MAX_LEN + 1)},
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ),
        ({"body": "UPDATED"}, status.HTTP_200_OK),
        ({"body": ""}, status.HTTP_422_UNPROCESSABLE_CONTENT),
    ],
)
async def test_update_post(
    authenticated_client, post_factory, payload, expected_status
):
    obj = await post_factory("post_to_update")
    response = await authenticated_client.patch(
        f"/api/v1/posts/{obj['id']}", json=payload
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        results = response.json()
        assert results["id"] == obj["id"]
        assert results["body"] == payload["body"]
        assert results["user"]["id"] == obj["user"]["id"]


@pytest.mark.asyncio
async def test_update_post_not_found(authenticated_client):
    response = await authenticated_client.patch(
        "/api/v1/posts/999", json={"body": "UPDATED"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "post_id, expected_status",
    [
        (1, status.HTTP_200_OK),
        (999, status.HTTP_404_NOT_FOUND),
    ],
)
async def test_delete_post(
    authenticated_client, post_factory, post_id, expected_status
):
    await post_factory("post")
    response = await authenticated_client.delete(f"/api/v1/posts/{post_id}")
    assert response.status_code == expected_status
