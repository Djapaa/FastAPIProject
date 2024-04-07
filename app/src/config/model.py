from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    """
        Базовый класс всех моделей
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
