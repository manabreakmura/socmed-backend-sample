from datetime import datetime

from pydantic import BaseModel, EmailStr

from posts.schemas import PostResponseSchema


class UserRequestSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    posts: list[PostResponseSchema]
    created_at: datetime
    updated_at: datetime
