from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel, Text

if TYPE_CHECKING:
    from users.models import User


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=64)
    body: str = Text()
    user_id: int = Field(default=None, foreign_key="users.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="posts")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
