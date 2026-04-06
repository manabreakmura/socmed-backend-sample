from typing import Annotated

from sqlmodel import Field

POST_BODY_MIN_LEN = 1
POST_BODY_MAX_LEN = 2000

PostBodyType = Annotated[
    str, Field(min_length=POST_BODY_MIN_LEN, max_length=POST_BODY_MAX_LEN)
]
