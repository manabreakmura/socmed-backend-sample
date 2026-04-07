import pytest
from fastapi import status

from src.users.schemas import UserRead


@pytest.mark.asyncio
async def test_get_user(authenticated_client, signup_obj):
    response = await authenticated_client.get(f"/api/v1/users/{signup_obj['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert (
        UserRead.model_validate(response.json()).model_dump()
        == UserRead.model_validate(signup_obj).model_dump()
    )
