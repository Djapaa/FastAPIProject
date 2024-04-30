import datetime
import secrets
import uuid

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select, or_, delete, Result
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi import HTTPException, Depends
from passlib.context import CryptContext

from .models import User, Token
from .schemas import UserCreateSerializer, oauth2_scheme
from .tasks import send_verification_mail
from ...config.database import get_async_session
from ...config.redis_conf import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_username_or_email(username: str, session: AsyncSession,
                                        email: str | None = None) -> Result.mappings:
    email = email if email else username
    query = (
        select(
            User.id,
            User.username,
            User.email,
            User.hashed_password,
            User.is_verified
        )
        .filter(
            or_(
                User.username == username,
                User.email == email
            )
        )
    )

    res = await session.execute(query)
    try:
        res = res.mappings().one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail='User with such email or login already exists')
    return res


async def get_user_by_token(token: str, session: AsyncSession):
    subq = (
        select(Token)
        .filter(
            Token.access_token == token,
            Token.expire_date > datetime.datetime.utcnow()
        ).subquery()
    )
    query = (
        select(User)
        # .options(
        #     selectinload(User.evaluated_and_bookmark_compositions)
        # )
        .filter(User.id == subq.c.user_id)
    )
    res = await session.execute(query)
    return res.scalar()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def redis_set_email_verification_key(email: EmailStr, uuid: str):
    """ Создание ключа:почты, в редис для верификации аккаунта"""
    await redis.set(uuid, email, 10 * 60)


async def redis_get_email_by_uuid(uuid: str):
    """Получение почты по токену"""
    return await redis.get(uuid)


async def user_registration(user: UserCreateSerializer, session: AsyncSession):
    if await get_user_by_username_or_email(user.username, session, user.email):
        raise HTTPException(status_code=400, detail='User with such email or login already exists')

    # Добавление нового юзера
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    session.add(new_user)
    await session.commit()

    # Отправка письма для верификации аккаунта нового пользователя
    verify_uuid = str(uuid.uuid4())
    await redis_set_email_verification_key(user.email, verify_uuid)
    send_verification_mail.delay(user.username, user.email, verify_uuid)
    return new_user


async def user_verify(uuid: str, session: AsyncSession):
    """
        Верификацияя аккаунта нового пользователя по токену(uuid)
    """
    email = await redis_get_email_by_uuid(uuid)
    if not email:
        raise HTTPException(status_code=400, detail="verify token is incorrect or expired")

    query = (
        select(User)
        .where(User.email == email)
    )
    res = await session.execute(query)
    res.scalar().is_verified = True
    await session.commit()


def get_token():
    return secrets.token_hex(32)


async def user_login(user_form: OAuth2PasswordRequestForm, session: AsyncSession, ):
    user = await get_user_by_username_or_email(user_form.username, session)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(
            plain_password=user_form.password,
            hashed_password=user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="User not active")

    # Получение и добавление токена в бд
    token = get_token()
    token_obj = Token(access_token=token, user_id=user.id)
    session.add(token_obj)
    await session.commit()
    return token


async def user_logout(session: AsyncSession,
                      token: Annotated[str, Depends(oauth2_scheme)]):
    # Удаление токена из бд
    stmt = (
        delete(Token)
        .filter(Token.access_token == token)
    )
    await session.execute(stmt)
    await session.commit()


async def get_current_user(session: Annotated[AsyncSession, Depends(get_async_session)],
                           token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_user_by_token(token, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_verify_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_stuff or current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=400, detail="Don't have permissions")
