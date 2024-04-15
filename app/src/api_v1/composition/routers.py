from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, File, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .services import create_new_composition, get_composition_detail, get_composition_list
from ...config.database import get_async_session
from .schemas import CompositionCreateSerializer, Paginator

router = APIRouter()


@router.get('/search/')
async def get_filtered_list_of_composition(session: Annotated[AsyncSession, Depends(get_async_session)], paginator: Paginator = Depends()):
    print(paginator)
    return await get_composition_list(session, paginator)

@router.get('/{id}/')
async def get_composition(id: int, session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await get_composition_detail(id, session)



@router.post('/')
async def create_composition(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        composition: CompositionCreateSerializer,
        image: UploadFile = File(...),

):
    await create_new_composition(composition, session, image)
    return Response(status_code=status.HTTP_201_CREATED)


@router.patch('/')
async def update_composition():
    pass
