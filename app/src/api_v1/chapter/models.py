from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, text, UniqueConstraint, ForeignKey

from ...config.model import Model
if TYPE_CHECKING:
    from ..composition.models import Composition

class Chapter(Model):
    __table_args__ = (UniqueConstraint('composition_id', 'number', name='uq_chapter_number_composition'),)
    __tablename__ = 'chapter'

    name: Mapped[str] = mapped_column(String(200), nullable=True)
    number: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                 onupdate=datetime.utcnow)

    is_published: Mapped[bool] = mapped_column(default=False)
    pub_date: Mapped[datetime] = mapped_column(nullable=True)

    composition_id: Mapped[int] = mapped_column(ForeignKey('composition.id'))
    composition: Mapped['Composition'] = relationship(back_populates='chapters')

    pages: Mapped[list['Page']] = relationship(back_populates='chapter')


class Page(Model):
    __table_args__ = (UniqueConstraint('number', 'chapter_id', name='uq_page_chapter_number'),)
    __tablename__ = 'page'
    number: Mapped[int]
    page_image: Mapped[str]

    chapter_id: Mapped[int] = mapped_column(ForeignKey('chapter.id'))
    chapter: Mapped['Chapter'] = relationship(back_populates='pages')









#     def save(self, *args, **kwargs):
#         if self.is_published and self.pub_date is None:
#             self.pub_date = timezone.now()
#         elif not self.is_published and self.pub_date is not None:
#             self.pub_date = None
#         super().save(*args, **kwargs)
#


