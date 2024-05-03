import datetime
from typing import Annotated
from decimal import Decimal

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from pydantic import EmailStr

from .models import GenderEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class UserCreateSerializer(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=100)]
    email: Annotated[EmailStr, Field(min_length=4, max_length=100)]
    password: Annotated[str, Field(min_length=4, max_length=100)]


class UserInfoSerializer(BaseModel):
    id: int
    username: Annotated[str, Field(min_length=4, max_length=100)]
    email: Annotated[EmailStr, Field(min_length=4, max_length=100)]
    is_stuff: bool
    is_superuser: bool
    is_verified: bool
    balance: Decimal
    descriptions: str | None
    gender: GenderEnum
    created_at: datetime.datetime
    email_not: bool
    avatar: str


