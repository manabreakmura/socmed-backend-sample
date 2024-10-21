from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=64, unique=True, index=True)
    password: str = Field(max_length=128)


class UserResponse(SQLModel):
    id: int
    email: str
    username: str


class Token(SQLModel):
    access_token: str
    token_type: str
