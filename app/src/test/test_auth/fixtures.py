from datetime import datetime

from ..conftest import test_async_session
import pytest
from ...api_v1.auth.models import User, Token
from ...api_v1.auth.services import get_password_hash


@pytest.fixture(scope='session')
async def create_verify_user():
    from .test_auth import mock_redis_set_email_verification_key
    dt = datetime(2024, 1, 1, hour=0,
                  minute=0, second=0, microsecond=0)
    async with test_async_session() as session:
        new_user = User(
            username='test',
            email='test@mail.ru',
            hashed_password=get_password_hash('12345'),
            is_verified=True,
            created_at=dt
        )
        session.add(new_user)
        try:
            await session.commit()
        except:
            await session.rollback()


@pytest.fixture(scope='session')
async def create_login_token_for_verify_user(create_verify_user):
    dt = datetime(2025, 1, 1, hour=0,
                  minute=0, second=0, microsecond=0)

    async with test_async_session() as session:
        new_user_login_token = Token(
            access_token='1q2w3e',
            user_id=1,
            expire_date=dt
        )
        session.add(new_user_login_token)
        await session.commit()

@pytest.fixture(scope='session')
async def create_unverified_user():
    from .test_auth import mock_redis_set_email_verification_key
    dt = datetime(2024, 1, 1, hour=0,
                  minute=0, second=0, microsecond=0)
    async with test_async_session() as session:
        new_user = User(
            username='test3',
            email='test3@mail.ru',
            hashed_password=get_password_hash('12345'),
            is_verified=False,
            created_at=dt
        )
        session.add(new_user)
        try:
            await session.commit()
            await mock_redis_set_email_verification_key('test3@mail.ru', 'test_uuid')
        except:
            await session.rollback()
