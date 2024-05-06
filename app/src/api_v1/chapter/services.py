from datetime import datetime

from fastapi import HTTPException, UploadFile, Request
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import TypeVar, Optional
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from itertools import zip_longest

from .models import Page, Chapter
from ..auth.models import User

from ..auth.services import get_user_by_token
from ..composition.models import Composition, UserCompositionRelation
from ..general_services import get_object, upload_image

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class ChapterCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, create_serializer: CreateSchemaType, composition_id: int):
        await get_object(self.session, composition_id, Composition)
        instance = Chapter(**create_serializer.dict(), composition_id=composition_id)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Chapter with such number already exists')
        return instance

    async def create_pages(self, files: list[UploadFile], chapter_id: int):
        await get_object(self.session, chapter_id, Chapter)
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

    async def pablish_chapter(self, chapter_id: int, publish: bool):
        """
            опубликовать или отменить публикацию, время публикации устанавливается после первой публикации
        """
        instance = await self.get(chapter_id)
        if instance.is_published:
            raise HTTPException(
                detail='Chapter already published',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if not instance.is_published and publish and not instance.pub_date:
            instance.is_published = True
            if not instance.pub_date:
                instance.pub_date = datetime.utcnow()
        instance.is_published = publish
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def get_published(self, chapter_id: int, current_user: Optional[User] = None):
        """
        Получить опубликованные главы, админы и персонал могут получить доступ к неопубликованным главам
        """
        chapter_instance = await self.get(chapter_id)
        if not chapter_instance.is_published:
            if current_user and (current_user.is_superuser or current_user.is_stuff):
                return chapter_instance
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        return chapter_instance

    async def get(self, chapter_id: int):
        query = (
            select(Chapter)
            .options(
                joinedload(Chapter.pages),
                joinedload(Chapter.composition)
            )
            .filter(Chapter.id == chapter_id)

        )
        chapter_instance = await self.session.scalar(query)
        if chapter_instance is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={
                                    f'detail': f'Chapter not found'
                                }
                                )

        return chapter_instance


async def get_current_user_for_chapter_crud(request: Request, session):
    header_auth = request.headers.get('Authorization', None)
    if not header_auth:
        return None
    prefix, token = header_auth.split()
    if prefix != 'Bearer':
        return None

    return await get_user_by_token(token, session)
