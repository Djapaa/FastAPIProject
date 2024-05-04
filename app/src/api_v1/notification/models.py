from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from ...config.model import Model

if TYPE_CHECKING:
    from ..auth.models import User


class UserNotification(Model):
    __tablename__ = 'user_notification'

    message: Mapped[str] = mapped_column(String(500))
    created: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='notification')

    type_id: Mapped[int] = mapped_column(ForeignKey('notification_type.id'))
    types: Mapped['NotificationType'] = relationship(back_populates='notification')


class NotificationType(Model):
    __tablename__ = 'notification_type'

    name: Mapped[str]
    notification: Mapped['UserNotification'] = relationship(back_populates='types')
