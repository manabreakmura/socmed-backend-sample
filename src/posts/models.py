from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlmodel import TIMESTAMP, Field, Relationship, SQLModel, func

if TYPE_CHECKING:
    from src.users.models import User


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    body: str = Field(min_length=1, max_length=500)
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    post_id: UUID = Field(foreign_key="posts.id", ondelete="CASCADE", index=True)
    created_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),  # ty: ignore
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )
    user: "User" = Relationship(  # noqa: UP037
        back_populates="comments", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Like(SQLModel, table=True):
    __tablename__ = "likes"

    post_id: UUID = Field(primary_key=True, foreign_key="posts.id", ondelete="CASCADE")
    user_id: UUID = Field(
        primary_key=True, foreign_key="users.id", ondelete="CASCADE", index=True
    )


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    body: str = Field(min_length=1, max_length=2000)
    created_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),  # ty: ignore
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    user: "User" = Relationship(  # noqa: UP037
        back_populates="posts", sa_relationship_kwargs={"lazy": "selectin"}
    )
    likes: list["User"] = Relationship(  # noqa: UP037
        back_populates="likes",
        link_model=Like,
    )
