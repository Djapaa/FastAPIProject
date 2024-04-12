import enum
from datetime import datetime

from sqlalchemy import String, text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...config.model import Model


class Composition(Model):
    __tablename__ = 'composition'
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    english_title: Mapped[str] = mapped_column(String(255))
    another_name_title: Mapped[str] = mapped_column(String(500))
    year_of_creations: Mapped[int] = mapped_column(default=1980)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                 onupdate=datetime.utcnow)
    descriptions: Mapped[str] = mapped_column(nullable=True)  # информация о пользователе
    composition_image: Mapped[str] = mapped_column(default='media/composition/default.png')
    view: Mapped[int] = mapped_column(default=0)
    count_rating: Mapped[int] = mapped_column(default=0)
    avg_rating: Mapped[Numeric] = mapped_column(Numeric(3, 1), default=0)
    count_bookmarks: Mapped[int] = mapped_column(default=0)
    total_votes: Mapped[int] = mapped_column(default=0)

    age_rating_id: Mapped[int] = mapped_column(ForeignKey('composition_age_rating.id'))
    age_rating: Mapped['CompositionsAgeRating'] = relationship(back_populates='composition')

    type_id: Mapped[int] = mapped_column(ForeignKey('composition_type.id'))
    type: Mapped['CompositionType'] = relationship(back_populates='composition')

    status_id: Mapped[int] = mapped_column(ForeignKey('composition_status.id'))
    status: Mapped['CompositionStatus'] = relationship(back_populates='composition')

    composition_genres: Mapped[list["CompositionGenre"]] = relationship(back_populates='genre_compositions',
                                                                        secondary='composition_genre_relation'
                                                                        )

    composition_tags: Mapped[list["CompositionGenre"]] = relationship(back_populates='tag_compositions',
                                                                      secondary='composition_tag_relation'
                                                                      )

    readers: Mapped[list["User"]] = relationship(back_populates='bookmarks_and_ratings',
                                                 secondary='user_composition_relation'
                                                 )


class CompositionsAgeRating(Model):
    __tablename__ = 'composition_age_rating'

    name: Mapped[str] = mapped_column(String(50))
    composition: Mapped[list['Composition']] = relationship(back_populates='age_rating')


class CompositionType(Model):
    __tablename__ = 'composition_type'

    name: Mapped[str] = mapped_column(String(20))
    composition: Mapped[list['Composition']] = relationship(back_populates='type')


class CompositionStatus(Model):
    __tablename__ = 'composition_status'

    name: Mapped[str] = mapped_column(String(20))
    composition: Mapped[list['Composition']] = relationship(back_populates='status')


class CompositionGenreRelation(Model):
    __tablename__ = 'composition_genre_relation'

    composition_id: Mapped[int] = mapped_column(ForeignKey("composition.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("composition_genre.id"), primary_key=True)


class CompositionGenre(Model):
    __tablename__ = 'composition_genre'

    name: Mapped[str] = mapped_column(String(50))
    genre_compositions: Mapped[list['Composition']] = relationship(back_populates='composition_genres',
                                                                   secondary='composition_genre_relation'
                                                                   )


class CompositionTagRelation(Model):
    __tablename__ = 'composition_tag_relation'

    composition_id: Mapped[int] = mapped_column(ForeignKey("composition.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("composition_tag.id"), primary_key=True)


class CompositionTag(Model):
    __tablename__ = 'composition_tag'

    name: Mapped[str] = mapped_column(String(50))
    tag_compositions: Mapped[list['Composition']] = relationship(back_populates='composition_tags',
                                                                 secondary='composition_tag_relation'
                                                                 )


class BookmarkEnum(enum.Enum):
    READING = 1
    WILL_READ = 2
    READED = 3
    ABANDONED = 4
    POSTPONED = 5


class RatingEnum(enum.Enum):
    TEN = 10
    NINE = 9
    EIGHT = 8
    SEVEN = 7
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2
    ONE = 1


class UserCompositionRelation(Model):
    __tablename__ = 'user_composition_relation'

    composition_id: Mapped[int] = mapped_column(ForeignKey("composition.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    bookmark: Mapped[BookmarkEnum] = mapped_column(nullable=True)
    rating: Mapped[RatingEnum] = mapped_column(nullable=True)
