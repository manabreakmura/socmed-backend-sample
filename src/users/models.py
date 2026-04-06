from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.posts.models import Post


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    email: str = Field(index=True, min_length=3, max_length=256, unique=True)
    username: str = Field(index=True, min_length=3, max_length=32, unique=True)
    hashed_password: str = Field(max_length=256)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    posts: list["Post"] = Relationship(back_populates="user", cascade_delete=True)
