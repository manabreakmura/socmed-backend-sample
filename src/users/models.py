from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base

if TYPE_CHECKING:
    from posts.models import Post


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(60))

    posts: Mapped[List["Post"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
