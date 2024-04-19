from fastapi import HTTPException, UploadFile, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import TypeVar, Type, Annotated
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from itertools import zip_longest

from .models import Page, Chapter
from ..composition.models import Composition
from ..composition.services import check_obj_in_db, upload_image
from ...config.database import get_async_session

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class ChapterCRUD:
    def __init__(self, session: AsyncSession, model: Type[Chapter]):
        self.session = session
        self.model = model

    async def create(self, create_serializer: CreateSchemaType, composition_id: int):
        await check_obj_in_db(self.session, composition_id, Composition)
        instance = self.model(**create_serializer.dict(), composition_id=composition_id)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Chapter with such number already exists')
        return instance

    async def create_pages(self, files: list[UploadFile], chapter_id: int):
        await check_obj_in_db(self.session, chapter_id, self.model)
        chapter_instance = await self.get(chapter_id)
        for new_files, current_files in zip_longest(enumerate(files, 1), chapter_instance.pages):
            if new_files and not current_files:
                num, file = new_files
                dest = await upload_image(file, f'chapter/{chapter_id}/')
                instance = Page(number=num, page_image=dest, chapter_id=chapter_id)
                self.session.add(instance)
                await self.session.commit()

            if new_files and current_files:
                num, file = new_files
                dest = await upload_image(file, f'chapter/{chapter_id}/')
                current_files.number = num
                current_files.page_image = dest
                self.session.add(current_files)
                await self.session.commit()

            if not new_files and current_files:
                await self.session.delete(current_files)
                await self.session.commit()

        await self.session.refresh(chapter_instance)
        return chapter_instance

    # async def pablish_chapter(self, chapter_id):
    #     instance = await self.get(chapter_id)



    async def get(self, chapter_id: int):
        await check_obj_in_db(self.session, chapter_id, self.model)
        query = (
            select(self.model)
            .options(
                joinedload(self.model.pages)
            )
            .filter(self.model.id == chapter_id)

        )
        chapter_instance = await self.session.execute(query)
        return chapter_instance.scalar()


