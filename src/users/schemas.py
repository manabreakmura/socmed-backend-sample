from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, SecretStr, field_validator
from sqlmodel import Field, SQLModel
from zxcvbn import zxcvbn


class UserCreate(SQLModel):
    email: EmailStr = Field(max_length=254)
    username: str = Field(max_length=64)
    password: SecretStr = Field(min_length=8, max_length=64)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        payload = value.get_secret_value()
        result = zxcvbn(payload)
        if result["score"] < 3:
            raise ValueError(" ".join(result["feedback"]["suggestions"]))
        return value


class UserRead(SQLModel):
    id: UUID
    email: EmailStr
    username: str
    created_at: datetime


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=254)
    username: str | None = Field(default=None, max_length=64)
