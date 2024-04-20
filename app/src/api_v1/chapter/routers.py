from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, File, Response, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .models import Chapter
from .services import ChapterCRUD, get_current_user_for_chapter_crud
from ..auth.models import User
from ..auth.schemas import UserInfoSerializer, oauth2_scheme
from ..auth.services import get_user_by_token, get_current_admin_user
from ...config.database import get_async_session

from .schemas import ChapterCreateSerializer, ChapterDetailSerializer, Publish

router = APIRouter()


@router.post('/{composition_id}/chapter/', status_code=201, dependencies=[Depends(get_current_admin_user)])
async def chapter_create(
        composition_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        chapter: ChapterCreateSerializer,
):
    chapter_crud = ChapterCRUD(session, Chapter)
    return await chapter_crud.create(chapter, composition_id)


@router.patch('/chapter/{id}/', dependencies=[Depends(get_current_admin_user)])
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
        request: Request
):
    current_user = await get_current_user_for_chapter_crud(request, session)
    chapter_crud = ChapterCRUD(session, Chapter)
    chapter_instance = await chapter_crud.get_published(id, current_user)
    return ChapterDetailSerializer.model_validate(chapter_instance, from_attributes=True)


@router.patch('/chapter/{id}/publish/', dependencies=[Depends(get_current_admin_user)])
async def publish_chapter(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        id: int,
        publish: Publish
):
    chapter_crud = ChapterCRUD(session, Chapter)
    chapter_instance = await chapter_crud.pablish_chapter(id, publish.publish)
    return ChapterDetailSerializer.model_validate(chapter_instance, from_attributes=True)
