from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def keyvalgen(obj):
    """ Generate attr name/val pairs, filtering out SQLA attrs."""
    excl = ('_sa_adapter', '_sa_instance_state')
    for k, v in vars(obj).items():
        if not k.startswith('_') and not any(hasattr(v, a) for a in excl):
            yield k, v


class Model(DeclarativeBase):
    """
        Базовый класс всех моделей
    """
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in keyvalgen(self))
        return f"{self.__class__.__name__}({params})"
