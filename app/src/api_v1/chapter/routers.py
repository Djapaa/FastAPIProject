from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, File, Response, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .models import Chapter
from .services import ChapterCRUD
from ..auth.schemas import UserInfoSerializer, oauth2_scheme
from ..auth.services import get_current_user
from ...config.database import get_async_session

from .schemas import ChapterCreateSerializer, ChapterDetailSerializer

router = APIRouter()


@router.post('/{composition_id}/chapter/', status_code=201)
async def chapter_create(
        composition_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        chapter: ChapterCreateSerializer,
):
    chapter_crud = ChapterCRUD(session, Chapter)
    return await chapter_crud.create(chapter, composition_id)


@router.patch('/chapter/{id}/')
async def chapter_pages_update(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        id: int,
        pages: list[UploadFile]
):
    chapter_crud = ChapterCRUD(session, Chapter)
    return await chapter_crud.create_pages(pages, id)

@router.get('/chapter/{id}/')
async def chapter_pages_update(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        id: int,
):
    chapter_crud = ChapterCRUD(session, Chapter)
    chapter_instance = await chapter_crud.get(id)
    return ChapterDetailSerializer.model_validate(chapter_instance, from_attributes=True)