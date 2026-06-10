from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import load_only
from sqlmodel import desc, select

from src.config.auth import auth_dep
from src.config.db import session_dep
from src.users.models import Follow, User
from src.users.schemas import UserRead, UserUpdate

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("", response_model=list[UserRead])
async def get_users(
    user_id: auth_dep,
    session: session_dep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[UserRead]:
    statement = select(User).order_by(desc(User.created_at)).offset(offset).limit(limit)
    result = await session.execute(statement)
    rows = result.scalars().all()
    return rows  # ty: ignore


@users_router.get("/{id}", response_model=UserRead)
async def get_user(
    id: UUID,
    user_id: auth_dep,
    session: session_dep,
) -> UserRead:
    statement = select(User).where(User.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return row  # ty: ignore


@users_router.patch("/{id}", response_model=UserRead)
async def update_user(
    id: UUID, payload: UserUpdate, user_id: auth_dep, session: session_dep
) -> UserRead:
    statement = select(User).where(User.id == id)
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(row, key):
            setattr(row, key, value)

    await session.commit()
    await session.refresh(row)
    return row  # ty: ignore


@users_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: UUID, user_id: auth_dep, session: session_dep) -> None:
    statement = (
        select(User).where(User.id == id).options(load_only(User.id))  # ty: ignore
    )

    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if row.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await session.delete(row)
    await session.commit()


@users_router.post("/{id}/follow")
async def follow(id: UUID, user_id: auth_dep, session: session_dep) -> dict[str, bool]:
    if user_id == id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    statement = select(select(User).where(User.id == id).exists())
    result = await session.execute(statement)
    row = result.scalar()

    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    statement = select(Follow).where(
        Follow.follower_id == user_id, Follow.following_id == id
    )
    result = await session.execute(statement)
    row = result.scalar()

    if row:
        await session.delete(row)
        following = False
    else:
        session.add(Follow(follower_id=user_id, following_id=id))
        following = True

    await session.commit()
    return {"following": following}
