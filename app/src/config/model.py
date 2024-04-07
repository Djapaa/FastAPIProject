
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    """
        Базовый класс всех моделей
    """

    id: Mapped[int] = mapped_column(primary_key=True)
