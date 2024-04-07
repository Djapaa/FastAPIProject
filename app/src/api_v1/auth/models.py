from sqlalchemy.orm import Mapped

from app.src.config.model import Model

class User(Model):
    name: Mapped[str]