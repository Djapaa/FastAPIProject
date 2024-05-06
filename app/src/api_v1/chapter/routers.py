from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .services import ChapterCRUD, get_current_user_for_chapter_crud
from ..auth.services import get_current_admin_user
from ..notification.tasks import send_notification_chapter_update

from ...config.database import get_async_session
from .schemas import ChapterCreateSerializer, ChapterDetailSerializer, Publish

router = APIRouter()


@router.post('/{composition_id}/chapter/', status_code=201, dependencies=[Depends(get_current_admin_user)])
async def chapter_create(
        composition_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        chapter: ChapterCreateSerializer,
):
    chapter_crud = ChapterCRUD(session)
    return await chapter_crud.create(chapter, composition_id)


@router.patch('/chapter/{id}/', dependencies=[Depends(get_current_admin_user)])
async def chapter_pages_update(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        id: int,
        pages: list[UploadFile]
):
    chapter_crud = ChapterCRUD(session)
    return await chapter_crud.create_pages(pages, id)


@router.get('/chapter/{id}/')
async def get_chapter(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        id: int,
        request: Request
):
    current_user = await get_current_user_for_chapter_crud(request, session)
    chapter_crud = ChapterCRUD(session)
    chapter_instance = await chapter_crud.get_published(id, current_user)
    return ChapterDetailSerializer.model_validate(chapter_instance, from_attributes=True)


@router.patch('/chapter/{chapter_id}/publish/', dependencies=[Depends(get_current_admin_user)], description='Публикация главы')
async def publish_chapter(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        chapter_id: int,
        publish: Publish
):
    chapter_crud = ChapterCRUD(session)
    chapter_instance = await chapter_crud.pablish_chapter(chapter_id, publish.publish)

    if publish.publish:
        message = f"Глава {chapter_instance.number} манги '{chapter_instance.composition.title}' была добавлена!"
        send_notification_chapter_update.delay(chapter_id, message)

    return ChapterDetailSerializer.model_validate(chapter_instance, from_attributes=True)
