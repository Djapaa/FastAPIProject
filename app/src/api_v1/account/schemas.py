from pydantic import BaseModel, Field

from ...api_v1.auth.models import GenderEnum


class UserPartialUpdateSerializer(BaseModel):
    username: str = Field(min_length=3, default=None)
    description: str = None
    email_not: bool = None
    gender: GenderEnum = None
