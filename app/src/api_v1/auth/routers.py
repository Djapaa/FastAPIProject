from typing import Annotated

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .models import User
from .schemas import UserSerializer, UserCreateSerializer, UserInfo
from .services import user_registration, user_login, get_current_user
from ...config.database import get_async_session

router = APIRouter()


@router.post('/signup/', status_code=201)
async def signup(user: UserCreateSerializer, session: Annotated[AsyncSession, Depends(get_async_session)]):
    """
        Регистрация пользователя
    """
    await user_registration(user, session)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/login')
async def login(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_form: OAuth2PasswordRequestForm = Depends()
):

    token = await user_login(user_form, session)
    return JSONResponse(
        content={"access_token": token},
        status_code=status.HTTP_200_OK
    )


@router.post('/logout/')
async def logout(
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    pass


@router.get("/current", response_model=UserInfo)
async def read_users_me(current_user: Annotated[UserInfo, Depends(get_current_user)]):
    return current_user
