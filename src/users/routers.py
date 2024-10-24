from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from config.auth import (
    authenticate,
    create_access_token,
    get_current_user,
    get_password_hash,
    oauth2_scheme,
    validate_email_or_raise,
)
from config.database import get_session
from users.models import Token, User

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post("/users/", response_model=User)
async def create_user(payload: User, session=Depends(get_session)):
    email = validate_email_or_raise(payload.email)

    try:
        user = User(
            email=email,
            username=payload.username,
            password=get_password_hash(payload.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )


@router.post("/auth/token", response_model=Token)
async def login(
    form_data=Depends(OAuth2PasswordRequestForm), session=Depends(get_session)
):
    user = authenticate(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(data={"sub": user.id}),
        "token_type": "bearer",
    }


@router.get("/users/", response_model=list[User])
async def get_all_users(session=Depends(get_session), auth=Depends(oauth2_scheme)):
    statement = select(User)
    return session.exec(statement).all()


@router.get("/users/{id}/", response_model=User)
async def get_user_by_id(id, session=Depends(get_session)):
    try:
        statement = select(User).where(User.id == id)
        return session.exec(statement).one()
    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )


@router.patch("/users/", response_model=User)
async def update_user(
    payload: User, session=Depends(get_session), token=Depends(oauth2_scheme)
):
    user = get_current_user(session, token)

    if not payload.id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if payload.username:
        user.username = payload.username

    if payload.email:
        user.email = validate_email_or_raise(payload.email)

    if payload.password:
        user.password = get_password_hash(payload.password)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )

    return user


@router.delete("/users/{id}/", response_model=User)
async def delete_user(id, session=Depends(get_session), token=Depends(oauth2_scheme)):
    try:
        statement = select(User).where(User.id == id)
        user = session.execute(statement).scalar_one()
        current_user = get_current_user(session, token)
        if not user.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        session.delete(user)
        session.commit()
        return user
    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )
