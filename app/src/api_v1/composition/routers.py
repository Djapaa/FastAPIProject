from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, File,  Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .services import create
from ...config.database import get_async_session
from .schemas import CompositionCreateSerializer

router = APIRouter()


@router.get('/search/')
async def get_filtered_list_of_composition():
    pass


@router.post('/')
async def create_composition(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        composition: CompositionCreateSerializer,
        image: UploadFile = File(...),

):
    await create(composition, session, image)
    return Response(status_code=status.HTTP_201_CREATED)


@router.patch('/')
async def update_composition():
    pass
