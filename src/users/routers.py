from datetime import timedelta

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from config.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate,
    create_access_token,
    get_password_hash,
    oauth2_scheme,
)
from config.database import get_session
from users.models import Token, User, UserResponse

router = APIRouter()


@router.post("/register/", tags=["users"], response_model=UserResponse)
async def register(payload: User, session=Depends(get_session)):
    try:
        email = validate_email(payload.email, check_deliverability=False)
        email = email.normalized
    except EmailNotValidError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )

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


@router.get("/users/", tags=["users"], response_model=list[UserResponse])
async def users(session=Depends(get_session), auth=Depends(oauth2_scheme)):
    statement = select(User)
    return session.exec(statement).all()


@router.post("/auth/token", tags=["users"], response_model=Token)
async def get_access_token(
    form_data=Depends(OAuth2PasswordRequestForm), session=Depends(get_session)
):
    user = authenticate(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
