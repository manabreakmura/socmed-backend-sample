from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from config.auth import get_password_hash
from config.database import get_session
from users.models import User

router = APIRouter()


@router.post("/signup/", tags=["users"], response_model=User)
async def signup(payload: User, session=Depends(get_session)):
    try:
        email = validate_email(payload.email, check_deliverability=False)
        email = email.normalized
    except EmailNotValidError as exception:
        raise HTTPException(status_code=400, detail=str(exception))

    try:
        new_user = User(
            email=email,
            username=payload.username,
            password=get_password_hash(payload.password),
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except SQLAlchemyError as exception:
        raise HTTPException(status_code=400, detail=str(exception))


@router.get("/users/", tags=["users"])
async def list_users(session=Depends(get_session)):
    statement = select(User)
    results = session.exec(statement).all()
    return results
