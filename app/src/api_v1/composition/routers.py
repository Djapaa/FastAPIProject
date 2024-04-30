from typing import Annotated

from fastapi import APIRouter, Depends

from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from .services import CompositionCRUD
from ..auth.schemas import UserInfoSerializer
from ..auth.services import get_current_user, get_current_admin_user
from ...config.database import get_async_session
from .schemas import CompositionCreateSerializer, Paginator, CompositionUpdateSerializer, RatingSerializer, \
    BookmarkSerializer, CompositionDetailSerializer, CompositionListSerializer
from .filters import CompositionFilter

router = APIRouter()


@router.get('/search/')
async def get_filtered_list_of_composition(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        paginator: Annotated[Paginator, Depends()],
        composition_filter: Annotated[CompositionFilter, FilterDepends(CompositionFilter)]
):
    composition_crud = CompositionCRUD(session)
    print(composition_filter)
    compositions = await composition_crud.get_paginate_and_filtered_list(paginator, composition_filter)
    return [CompositionListSerializer.model_validate(composition, from_attributes=True) for composition in compositions]


@router.get('/{id}/')
async def get_composition(id: int, session: Annotated[AsyncSession, Depends(get_async_session)]):
    composition_crud = CompositionCRUD(session)
    composition = await composition_crud.get(id)
    return CompositionDetailSerializer.model_validate(composition, from_attributes=True)


@router.post('/', status_code=201)
async def create_composition(
        session: Annotated[AsyncSession, Depends(get_current_admin_user)],
        composition: CompositionCreateSerializer,

):
    composition_crud = CompositionCRUD(session)
    return await composition_crud.create(composition)


@router.patch('/{id}/')
async def update_composition(
        id: int,
        session: Annotated[AsyncSession, Depends(get_current_admin_user)],
        composition: CompositionUpdateSerializer,

):
    composition_crud = CompositionCRUD(session)
    return await composition_crud.partial_update(id, composition)


@router.post('/{composition_id}/rating/')
async def composition_rating_add_or_update(
        composition_id: int,
        current_user: Annotated[UserInfoSerializer, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        rating: RatingSerializer,
):
    print(rating.vote)
    print(100 * '1')
    composition_crud = CompositionCRUD(session)
    return await composition_crud.rating_add(composition_id, current_user.id, rating.vote)


@router.post('/{composition_id}/bookmark/')
async def composition_bookmark_add_or_update(
        composition_id: int,
        current_user: Annotated[UserInfoSerializer, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        bookmark: BookmarkSerializer,
):
    composition_crud = CompositionCRUD(session)
    return await composition_crud.bookmark_add(composition_id, current_user.id, bookmark.vote)
