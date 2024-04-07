from sqlalchemy.orm import Mapped

from app.src.config.model import Model

class User(Model):
    __tablename__ = 'user'

    name: Mapped[str]
