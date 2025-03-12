from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from config.auth import create_access_token, verify_password
from config.database import session_dependency
from models.users import User

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/token")
def login(
    session: session_dependency, data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    statement = select(User).filter(User.username == data.username)
    user = session.exec(statement).one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
