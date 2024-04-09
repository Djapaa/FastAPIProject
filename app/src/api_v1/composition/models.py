from sqlalchemy.orm import Mapped

from app.src.config.model import Model

class Composition(Model):
    __tablename__ = 'composition'
    name: Mapped[str]
