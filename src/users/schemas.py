from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserRead(SQLModel):
    id: int
    username: str


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=32)
    password: str = Field(min_length=8, max_length=128)
