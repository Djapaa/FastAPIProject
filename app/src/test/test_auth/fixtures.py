from ..conftest import test_async_session
import pytest
from ...api_v1.auth.models import User
from ...api_v1.auth.services import get_password_hash


@pytest.fixture(scope='session')
async def create_user():
    async with test_async_session() as session:
        new_user = User(
            username='test',
            email='test@mail.ru',
            hashed_password=get_password_hash('test'),
            is_verified=True
        )
        session.add(new_user)
        await session.commit()