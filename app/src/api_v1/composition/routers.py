from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, File, Response, Query
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .services import create_new_composition, get_composition_detail, get_composition_list, partial_update_composition, \
    rating_add, bookmark_add
from ..auth.schemas import UserInfoSerializer
from ..auth.services import get_current_user
from ...config.database import get_async_session
from .schemas import CompositionCreateSerializer, Paginator, CompositionUpdateSerializer, RatingSerializer, \
    BookmarkSerializer
from .filters import CompositionFilter

router = APIRouter()


@router.get('/search/')
async def get_filtered_list_of_composition(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        paginator: Paginator = Depends(),
        composition_filter: CompositionFilter = FilterDepends(CompositionFilter)
):
    return await get_composition_list(session, paginator, composition_filter)


@router.get('/{id}/')
async def get_composition(id: int, session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await get_composition_detail(id, session)


@router.post('/')
async def create_composition(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        composition: CompositionCreateSerializer,

):
    await create_new_composition(composition, session)
    return Response(status_code=status.HTTP_201_CREATED)


@router.patch('/{id}/')
async def update_composition(
        id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        composition: CompositionUpdateSerializer,

):
    return await partial_update_composition(id, session, composition)


@router.post('/{id}/rating/')
async def composition_rating_add_or_update(id: int,
                                           current_user: Annotated[UserInfoSerializer, Depends(get_current_user)],
                                           session: Annotated[AsyncSession, Depends(get_async_session)],
                                           rating: RatingSerializer,
                                           ):
    return await rating_add(id, current_user.id, session, rating.vote)


@router.post('/{id}/bookmark/')
async def composition_bookmark_add_or_update(id: int,
                                             current_user: Annotated[UserInfoSerializer, Depends(get_current_user)],
                                             session: Annotated[AsyncSession, Depends(get_async_session)],
                                             bookmark: BookmarkSerializer,
                                             ):
    return await bookmark_add(id, current_user.id, session, bookmark.vote)

