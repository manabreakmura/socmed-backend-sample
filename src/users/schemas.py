from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    password: str


class UserRead(SQLModel):
    id: int
    username: str
