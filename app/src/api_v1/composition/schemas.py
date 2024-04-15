import json
from decimal import Decimal
from typing import Any, Annotated
from slugify import slugify
from pydantic import BaseModel, Field, field_validator, computed_field, model_validator
from sqlalchemy import Numeric


class CompositionAdditionalInfo(BaseModel):
    id: int
    name: str


class CompositionStatusSerializer(CompositionAdditionalInfo):
    pass


class CompositionTypeSerializer(CompositionAdditionalInfo):
    pass


class CompositionAgeratingSerializer(CompositionAdditionalInfo):
    pass


class CompositionTagSerializer(CompositionAdditionalInfo):
    pass


class CompositionGenreSerializer(CompositionAdditionalInfo):
    pass


class CompositionCreateSerializer(BaseModel):
    title: str
    english_title: str
    another_name_title: str | None
    year_of_creations: int = Field(ge=1980)
    descriptions: str | None
    status: int
    type: int
    age_rating: int

    genres: list[int]
    tags: list[int]

    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.title)

    @model_validator(mode="before")
    @classmethod
    def to_py_dict(cls, data):
        return json.loads(data)


class CompositionListSerializer(BaseModel):
    slug: str
    title: str
    composition_image: str
    type: CompositionTypeSerializer
    avg_rating: int

    class Config:
        from_attributes = True


class CompositionDetailSerializer(BaseModel):
    slug: str
    title: str
    composition_image: str
    type: CompositionTypeSerializer
    avg_rating: int
    english_title: str
    another_name_title: str | None
    year_of_creations: int = Field(ge=1980)
    descriptions: str | None
    status: CompositionStatusSerializer
    age_rating: CompositionAgeratingSerializer
    composition_genres: list[CompositionGenreSerializer]
    composition_tags: list[CompositionTagSerializer]
    view: int
    count_rating: int
    avg_rating: Decimal
    count_bookmarks: int
    total_votes: int

    class Config:
        from_attributes = True


class Paginator(BaseModel):
    page: Annotated[int, Field(ge=1, default=1)]
    page_size: Annotated[int, Field(ge=1, le=100, default=20)]

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

