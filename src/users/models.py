from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid7

from sqlmodel import TIMESTAMP, Field, Relationship, SQLModel, func

from src.posts.models import Like

if TYPE_CHECKING:
    from src.posts.models import Post


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        sa_column_kwargs={"server_default": func.uuidv7()},
    )
    email: str = Field(max_length=254, index=True, unique=True)
    username: str = Field(max_length=64, index=True, unique=True)
    hashed_password: str = Field(max_length=254)
    created_at: datetime = Field(
        sa_type=TIMESTAMP(timezone=True),  # ty: ignore
        sa_column_kwargs={"server_default": func.current_timestamp()},
    )
    posts: list["Post"] = Relationship(  # noqa: UP037
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    likes: list["Post"] = Relationship(  # noqa: UP037
        back_populates="likes", link_model=Like
    )
