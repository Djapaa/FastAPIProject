from typing import Optional

from fastapi import Query
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from .models import Composition, CompositionType, CompositionStatus, CompositionsAgeRating, CompositionTag, \
    CompositionGenre


class TypeFilter(Filter):
    id__in: Optional[list[int]] = Query(default=None, alias='types')

    class Constants(Filter.Constants):
        model = CompositionType


class StatusFilter(Filter):
    id__in: Optional[list[int]] = Query(default=None, alias='status')

    class Constants(Filter.Constants):
        model = CompositionStatus


class AgeratingFilter(Filter):
    id__in: Optional[list[int]] = Query(default=None, alias='age_ratings')

    class Constants(Filter.Constants):
        model = CompositionsAgeRating


class TagFilter(Filter):
    id__in: Optional[list[int]] = Query(default=None, alias='tags')

    class Constants(Filter.Constants):
        model = CompositionTag


class GenreFilter(Filter):
    id__in: Optional[list[int]] = Query(default=None, alias='genres')

    class Constants(Filter.Constants):
        model = CompositionGenre


class CompositionFilter(Filter):
    type: Optional[TypeFilter] = FilterDepends(with_prefix("type", TypeFilter), by_alias=False)
    status: Optional[StatusFilter] = FilterDepends(with_prefix("status", StatusFilter))
    age_rating: Optional[AgeratingFilter] = FilterDepends(with_prefix("age_rating", AgeratingFilter))

    genres: Optional[GenreFilter] = FilterDepends(with_prefix("genre", GenreFilter))
    tags: Optional[TagFilter] = FilterDepends(with_prefix("tag", TagFilter))

    year_of_creations__gte: Optional[int] = None
    year_of_creations__lte: Optional[int] = None

    order_by: Optional[list[str]] = ['-created_at']

    class Constants(Filter.Constants):
        model = Composition
