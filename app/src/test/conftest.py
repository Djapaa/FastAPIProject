import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import sys

sys.path = ['', '..'] + sys.path[1:]
from app.src.config.settings import settings
from app.src.config.model import Model
from app.src.config.database import get_async_session, engine
from app.src.main import app

test_engine = create_async_engine(str(settings.ASYNC_TEST_DATABASE_URI),
                                  echo=settings.ECHO)

test_async_session = sessionmaker(test_engine,
                                  class_=AsyncSession,
                                  expire_on_commit=False)

Model.metadata.bind = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

@pytest.fixture(autouse=True, scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as ac:
        yield ac
