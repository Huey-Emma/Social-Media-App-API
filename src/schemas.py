import re
import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserSchema(BaseModel):
    username: str
    email: EmailStr


class UserSchemaIn(UserSchema):
    password: str

    @validator('password')
    @classmethod
    def validate_password(cls, value):
        pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,24}$')
        err_message = """
        Password must be at least 8 characters long and must contain at least one capital letter, small letter and digit
        """
        if not pattern.match(value):
            raise ValueError(err_message)
        return value


class UserSchemaOut(UserSchema):
    id: int
    created: datetime.datetime


class PostSchema(BaseModel):
    title: str
    content: str


class PostSchemaIn(PostSchema):
    published: Optional[bool] = True


class PostSchemaOut(PostSchema):
    id: int
    published: bool
    likes: int
    created: datetime.datetime


class PostUserSchemaOut(PostSchemaOut):
    user: UserSchemaOut


class VoteSchema(BaseModel):
    post_id: int
    direction: int


class VoteSchemaIn(VoteSchema):
    @validator('direction')
    @classmethod
    def validate_direction(cls, value):
        if not (0 <= value <= 1):
            raise ValueError('Vote direction can only be zero or one')
        return value

