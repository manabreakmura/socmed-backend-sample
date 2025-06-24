from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=32)
    password: str = Field(min_length=8, max_length=128)


class UserRead(SQLModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
