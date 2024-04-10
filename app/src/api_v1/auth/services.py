import datetime
from typing import Annotated

from fastapi import HTTPException, Depends
import secrets

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .models import User, Token
from .schemas import UserSerializer, UserCreateSerializer, oauth2_scheme, UserInfo
from passlib.context import CryptContext

from ...config.database import get_async_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_username_or_email(username: str, session: AsyncSession, email: str | None = None):
    email = email if email else username
    query = (
        select(
            User.id,
            User.username,
            User.email,
            User.hashed_password
        )
        .filter(
            or_(
                User.username == username,
                User.email == email
            )
        )
    )
    res = await session.execute(query)
    return res.mappings().one_or_none()


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
        .filter(User.id == subq.c.user_id)
    )
    res = await session.execute(query)
    return res.scalar()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def user_registration(user: UserCreateSerializer, session: AsyncSession):
    if await get_user_by_username_or_email(user.username, session, user.email):
        raise HTTPException(status_code=400, detail='User already exists')

    insert_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    session.add(insert_user)
    await session.commit()


def get_token():
    return secrets.token_hex(32)


async def user_login(user_form: OAuth2PasswordRequestForm, session: AsyncSession,):
    user = await get_user_by_username_or_email(user_form.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(
            plain_password=user_form.password,
            hashed_password=user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = get_token()
    token_obj = Token(access_token=token, user_id=user.id)
    session.add(token_obj)
    await session.commit()
    return token


def to_pydantic(db_object, pydantic_model):
    return pydantic_model(**db_object.__dict__)


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
