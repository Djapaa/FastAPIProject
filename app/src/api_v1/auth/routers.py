import uuid
from typing import Annotated

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import UserCreateSerializer, UserInfoSerializer, oauth2_scheme
from .services import user_registration, user_login, user_logout, user_verify, get_current_user
from ...config.database import get_async_session

router = APIRouter()


@router.post('/signup/', status_code=201)
async def signup(user: UserCreateSerializer, session: Annotated[AsyncSession, Depends(get_async_session)]):
    """
        Регистрация пользователя
    """
    user = await user_registration(user, session)
    return UserInfoSerializer.model_validate(user, from_attributes=True)


@router.post('/login/', status_code=200)
async def login(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_form: OAuth2PasswordRequestForm = Depends()
):
    token = await user_login(user_form, session)
    return JSONResponse(
        content={
            "access_token": token,
            'type': 'bearer'
        },
        status_code=status.HTTP_200_OK
    )


@router.post('/logout/', status_code=204, dependencies=[Depends(get_current_user)])
async def logout(session: Annotated[AsyncSession, Depends(get_async_session)],
                 token: Annotated[str, Depends(oauth2_scheme)]
                 ):
    await user_logout(session, token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/current/', response_model=UserInfoSerializer)
async def read_users_me(current_user: Annotated[UserInfoSerializer, Depends(get_current_user)]):
    return current_user


@router.post('/verify/{user_verify_uuid}/')
async def user_account_verification(user_verify_uuid, session: Annotated[AsyncSession, Depends(get_async_session)]):
    await user_verify(user_verify_uuid, session)
    return Response(status_code=status.HTTP_200_OK)
