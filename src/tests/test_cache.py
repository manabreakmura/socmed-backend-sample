import pytest
from fastapi import status

from src.posts.schemas import PostRead


@pytest.mark.asyncio
async def test_cache_delete_on_post_update(authenticated_client, post_factory, cache):
    obj = await post_factory("post")

    cache_key, cache_value = "post", obj["id"]
    cache_obj = PostRead.model_validate(obj)
    await cache.set_(cache_key, cache_value, cache_obj.model_dump_json())

    response = await authenticated_client.patch(
        f"/api/v1/posts/{obj['id']}", json={"body": "UPDATED"}
    )
    assert response.status_code == status.HTTP_200_OK

    cached = await cache.get_(cache_key, cache_value)
    assert cached is None


@pytest.mark.asyncio
async def test_cache_delete_on_post_delete(authenticated_client, post_factory, cache):
    obj = await post_factory("post")

    cache_key, cache_value = "post", obj["id"]
    cache_obj = PostRead.model_validate(obj)
    await cache.set_(cache_key, cache_value, cache_obj.model_dump_json())

    response = await authenticated_client.delete(f"/api/v1/posts/{obj['id']}")
    assert response.status_code == status.HTTP_200_OK

    cached = await cache.get_(cache_key, cache_value)
    assert cached is None
