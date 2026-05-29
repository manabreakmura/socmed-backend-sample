from datetime import datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from src.users.schemas import UserRead


class PostCreate(SQLModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body", mode="before")
    @classmethod
    def validate_body(cls, value: str) -> str:
        return value.strip()


class PostUpdate(SQLModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body", mode="before")
    @classmethod
    def validate_body(cls, value: str) -> str:
        return value.strip()


class PostRead(SQLModel):
    id: UUID
    body: str
    created_at: datetime
    user: UserRead
    total_likes: int
    is_liked: bool


class CommentRead(SQLModel):
    id: UUID
    body: str
    created_at: datetime
    user: UserRead


class CommentCreate(SQLModel):
    body: str = Field(min_length=1, max_length=500)

    @field_validator("body", mode="before")
    @classmethod
    def validate_body(cls, value: str) -> str:
        return value.strip()
