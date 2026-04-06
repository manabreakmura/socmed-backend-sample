from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.users.models import User

from src.posts.types import PostBodyType


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: int = Field(primary_key=True)
    body: PostBodyType
    user_id: int = Field(index=True, foreign_key="users.id", ondelete="CASCADE")
    user: "User" = Relationship(
        back_populates="posts", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
