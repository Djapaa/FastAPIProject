import asyncio
from abc import ABC, abstractmethod

from celery import shared_task
from sqlalchemy import select


from .models import UserNotification, NotificationType
from ..auth.models import User

from ..composition.services import get_composition_readers
from ..general_services import send_mail_async
from ...config.database import async_session


class BaseNotificator(ABC):
    @abstractmethod
    async def send_notification(self, readers: list[User], message):
        raise NotImplemented()


class ChapterUpdateWebNotification(BaseNotificator):
    async def send_notification(self, readers: list[User], message):
        async with async_session() as session:
            query = (
                select(
                    NotificationType
                )
                .filter(
                    NotificationType.name == 'Обновления'
                )
            )
            notification_type_instance = await session.scalar(query)
            if notification_type_instance is None:
                notification_type_instance = NotificationType(name='Обновления')
                session.add(notification_type_instance)
                await session.commit()
                await session.refresh(notification_type_instance)
            session.add_all(
                [
                    UserNotification(
                        user_id=reader.id,
                        type_id=notification_type_instance.id,
                        message=message
                    )
                    for reader in readers
                ]
            )
            await session.commit()


class ChapterUpdateEmailNotification(BaseNotificator):
    async def send_notification(self, readers: list[User], message):
        readers = [reader.email for reader in readers if reader.email_not]
        await send_mail_async(
            readers,
            'Выход новой главы на "Абстрактное название сайта"',
            message
        )


class Notificator(BaseNotificator):
    def __init__(self, notificators: list[BaseNotificator]):
        self.notificators = notificators

    async def send_notification(self, reader: list[User], message):
        for notificator in self.notificators:
            await notificator.send_notification(reader, message)



@shared_task(name='send_notification_about_new_chapter')
def send_notification_chapter_update(chapter_id: int, message: str):
    """

    """
    notificator = Notificator(
        [ChapterUpdateWebNotification(), ChapterUpdateEmailNotification()]
    )

    loop = asyncio.get_event_loop()
    readers = loop.run_until_complete(get_composition_readers(chapter_id))
    return loop.run_until_complete(notificator.send_notification(readers, message))
