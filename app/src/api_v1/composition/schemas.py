import json
from typing import Any
from slugify import slugify
from pydantic import BaseModel, Field, field_validator, computed_field, model_validator


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


