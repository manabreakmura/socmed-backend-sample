import pytest
from fastapi import status

pytestmark = pytest.mark.anyio


class TestPost:
    async def test_create_success(self, authenticated_client):
        response = await authenticated_client.post(
            "/api/v1/posts", json={"body": "test-post"}
        )
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["body"] == "test-post"

    async def test_create_no_auth_fail(self, client):
        response = await client.post(
            "/api/v1/posts", json={"body": "test-no-auth-post"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_empty_fail(self, authenticated_client):
        response = await authenticated_client.post("/api/v1/posts", json={"body": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_get_all_success(self, authenticated_client, post_obj):
        response = await authenticated_client.get("/api/v1/posts")
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result[0]["body"] == post_obj["body"]

    async def test_get_no_auth_fail(self, client):
        response = await client.get("/api/v1/posts")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_success(self, authenticated_client, post_obj):
        response = await authenticated_client.patch(
            f"/api/v1/posts/{post_obj['id']}", json={"body": "updated"}
        )
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["body"] == "updated"
        assert result["user"] == post_obj["user"]

    async def test_delete_success(self, authenticated_client, post_obj):
        response = await authenticated_client.delete(f"/api/v1/posts/{post_obj['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_no_auth_fail(self, client, post_obj):
        response = await client.delete(f"/api/v1/posts/{post_obj['id']}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLike:
    async def test_success(self, authenticated_client, post_obj):
        assert (
            await authenticated_client.post(f"/api/v1/posts/{post_obj['id']}/like")
        ).json() == {"is_liked": True}

        response = await authenticated_client.get(f"/api/v1/posts/{post_obj['id']}")
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["total_likes"] > 0
        assert result["is_liked"] is True

    async def test_no_auth_fail(self, client, post_obj):
        response = await client.post(f"/api/v1/posts/{post_obj['id']}/like")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_not_found_fail(self, authenticated_client):
        response = await authenticated_client.post(
            "/api/v1/posts/00000000-0000-0000-0000-000000000000/like"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_success(self, authenticated_client, post_obj):
        assert (
            await authenticated_client.post(f"/api/v1/posts/{post_obj['id']}/like")
        ).json() == {"is_liked": True}

        assert (
            await authenticated_client.post(f"/api/v1/posts/{post_obj['id']}/like")
        ).json() == {"is_liked": False}

        response = await authenticated_client.get(f"/api/v1/posts/{post_obj['id']}")
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["total_likes"] == 0
        assert result["is_liked"] is False


class TestComment:
    async def test_create_success(self, authenticated_client, post_obj):
        response = await authenticated_client.post(
            f"/api/v1/posts/{post_obj['id']}/comments",
            json={"body": "test-comment"},
        )
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result["body"] == "test-comment"

    async def test_get_success(self, authenticated_client, post_obj, comment_obj):
        response = await authenticated_client.get(
            f"/api/v1/posts/{post_obj['id']}/comments"
        )
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        assert result[0]["body"] == comment_obj["body"]

    async def test_delete_success(self, authenticated_client, post_obj, comment_obj):
        assert (
            await authenticated_client.delete(
                f"/api/v1/posts/{post_obj['id']}/comments/{comment_obj['id']}"
            )
        ).status_code == status.HTTP_204_NO_CONTENT
