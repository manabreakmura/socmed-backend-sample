from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_email
from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def validate_email(email):
    try:
        return _validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exception.args)
