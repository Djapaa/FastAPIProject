from datetime import datetime
from pydantic import BaseModel

class Publish(BaseModel):
    publish: bool

class PageCreateSerializer(BaseModel):
    page_image: str


class ChapterCreateSerializer(BaseModel):
    name: str
    number: int


class PageDetailSerializer(PageCreateSerializer):
    number: int


class ChapterDetailSerializer(ChapterCreateSerializer):
    is_published: bool
    pub_date: datetime | None
    pages: list[PageDetailSerializer]
