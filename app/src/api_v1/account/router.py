from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from .services import UserCRUD
from .schemas import UserPartialUpdateSerializer
from ..auth.models import User
from ..auth.schemas import UserInfoSerializer
from ..auth.services import get_current_user
from ...config.database import get_async_session

router = APIRouter()


@router.patch('/{user_id}/')
async def update_user(
        user_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        updated_data: UserPartialUpdateSerializer
):
    user_crud = UserCRUD(session)
    return await user_crud.partial_update(user_id, updated_data, current_user)

@router.patch('/{user_id}/avatar/')
async def update_user_avatar(
        user_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        image: UploadFile,
        current_user: Annotated[User, Depends(get_current_user)]

):
    user_crud = UserCRUD(session)
    return await user_crud.update_avatar(user_id, image, current_user)


@router.get('/{user_id}/')
async def get_user(
        user_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user_crud = UserCRUD(session)
    return await user_crud.get(user_id)

