import enum
from datetime import datetime

from pydantic import EmailStr, Field
from sqlalchemy import String, Numeric, text, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from ...config.model import Model


if TYPE_CHECKING:
    from ..composition.models import Composition


class GenderEnum(str, enum.Enum):
    female = "female"
    male = "male"
    not_specified = "Not specified"


class User(Model):
    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_stuff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    balance: Mapped[Numeric] = mapped_column(Numeric(6, 2), default=0)
    descriptions: Mapped[str | None] = mapped_column(String(500), nullable=True)  # информация о пользователе
    gender: Mapped[GenderEnum] = mapped_column(default=GenderEnum.not_specified)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                 onupdate=datetime.utcnow)

    email_not: Mapped[bool] = mapped_column(default=False)

    avatar: Mapped[str] = mapped_column(default='media/user/default.png')

    hashed_password: Mapped[str]

    tokens: Mapped[list['Token']] = relationship(back_populates="user")

    evaluated_and_bookmark_compositions: Mapped[list["Composition"]] = relationship(back_populates='readers',
                                                                                   secondary='user_composition_relation'
                                                                                   )


class Token(Model):
    __tablename__ = 'token'

    access_token: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    expire_date: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now()) + INTERVAL '14 day'"))

    user: Mapped['User'] = relationship(back_populates="tokens")
