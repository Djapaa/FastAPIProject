from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings

# Создание асинхронного движка
engine = create_async_engine(str(settings.ASYNC_DATABASE_URI),
                             echo=settings.ECHO)

async_session = sessionmaker(engine,
                             class_=AsyncSession,
                             expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
