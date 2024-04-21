from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from ...config.model import Model

if TYPE_CHECKING:
    from ..chapter.models import Chapter
    from ..auth.models import User

class LikeDislike(Model):
    __tablename__ = 'like_dislike'

    vote: Mapped[int]

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='voted')

    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapter.id'), nullable=True, default=None)
    liked_chapter: Mapped['Chapter'] = relationship(back_populates='votes')