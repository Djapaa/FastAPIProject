from decimal import Decimal

from pydantic import BaseModel, Field
from datetime import datetime

from ...api_v1.auth.models import GenderEnum


class UserPartialUpdateSerializer(BaseModel):
    username: str = Field(min_length=3, default=None)
    descriptions: str = None
    email_not: bool = None
    gender: GenderEnum = None

class UserGetSerializer(UserPartialUpdateSerializer):
    is_stuff: bool
    is_superuser: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    balance: Decimal
    count_voted: int
    avatar: str
