from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import exists, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.users.models import Follow, User
from src.users.schemas import UserRead, UserUpdate

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("", response_model=list[UserRead])
async def search(
    me: auth_dep,
    session: session_dep,
    search: Annotated[str, Query(min_length=1, max_length=64)],
) -> list[UserRead]:
    statement = (
        select(
            User,
            exists()
            .where(Follow.follower_id == me, Follow.following_id == User.id)  # ty: ignore
            .correlate(User)
            .label("is_following"),
        )
        .where(User.username.icontains(search, autoescape=True), User.id != me)  # ty: ignore
        .order_by(User.username)
    ).limit(20)
    result = await session.execute(statement)
    rows = result.all()

    return [
        UserRead(
            id=row.id,
            username=row.username,
            created_at=row.created_at,
            is_following=is_following,
        )
        for row, is_following in rows
    ]


@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    me: auth_dep,
    session: session_dep,
) -> UserRead:
    statement = select(
        User,
        exists()
        .where(Follow.follower_id == me, Follow.following_id == user_id)  # ty: ignore
        .correlate(User)
        .label("is_following"),
    ).where(User.id == user_id)
    result = await session.execute(statement)
    row = result.one_or_none()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    row, is_following = row

    return UserRead(
        id=row.id,
        username=row.username,
        created_at=row.created_at,
        is_following=is_following,
    )


@users_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID, payload: UserUpdate, me: auth_dep, session: session_dep
) -> UserRead:
    row = await session.get(User, user_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.id != me:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)

    await session.commit()
    await session.refresh(row)

    return row  # ty: ignore


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, me: auth_dep, session: session_dep) -> None:
    row = await session.get(User, user_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.id != me:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()


@users_router.post("/{user_id}/follow")
async def add_follow(
    user_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    if user_id == me:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    row = await session.get(User, user_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Follow).where(
        Follow.follower_id == me, Follow.following_id == user_id
    )
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        session.add(Follow(follower_id=me, following_id=user_id))
        await session.commit()

    return {"following": True}


@users_router.delete("/{user_id}/follow")
async def delete_follow(
    user_id: UUID, me: auth_dep, session: session_dep
) -> dict[str, bool]:
    if user_id == me:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    row = await session.get(User, user_id)

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Follow).where(
        Follow.follower_id == me, Follow.following_id == user_id
    )
    result = await session.execute(statement)
    row = result.scalar()

    if row:
        await session.delete(row)
        await session.commit()

    return {"following": False}
