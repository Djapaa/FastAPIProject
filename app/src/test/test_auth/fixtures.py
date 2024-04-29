from datetime import datetime

from ..conftest import test_async_session
import pytest
from ...api_v1.auth.models import User, Token
from ...api_v1.auth.services import get_password_hash


@pytest.fixture(scope='session')
async def create_user():
    async with test_async_session() as session:
        new_user = User(
            username='test',
            email='test@mail.ru',
            hashed_password=get_password_hash('12345'),
            is_verified=True
        )
        session.add(new_user)
        await session.commit()


@pytest.fixture(scope='session')
async def create_login_user(create_user):
    dt = datetime(2024, 1, 1, hour=0,
                  minute=0, second=0, microsecond=0)

    async with test_async_session() as session:
        new_user_login_token = Token(
            access_token='1q2w3e',
            user_id=1,
            expire_date=dt
        )
        session.add(new_user_login_token)
        await session.commit()