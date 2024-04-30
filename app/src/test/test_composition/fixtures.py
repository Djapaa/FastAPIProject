from datetime import datetime
from ...api_v1.composition.models import Composition, CompositionType, CompositionStatus, CompositionsAgeRating, \
    CompositionTag, CompositionGenre

from sqlalchemy.ext.asyncio import AsyncSession
from ..conftest import test_async_session
from typing import Type
from ...config.model import Model
import pytest


async def create_test_data(datas: list[dict], model: Type[Model]):
    session: AsyncSession
    objs = []
    async with test_async_session() as session:
        for data in datas:
            new_obj = model(**data)
            session.add(new_obj)
            await session.commit()
            objs.append(new_obj)
        return objs

async def create_test_age_ratings():
    datas = [
        {'name': '16+'},
        {'name': '18+'},
        {'name': 'Для всех'}
    ]
    return await create_test_data(datas, CompositionsAgeRating)


async def create_test_statuses():
    datas = [
        {'name': 'Продолжается'},
        {'name': 'Заморожен'},
        {'name': 'Закончен'}
    ]
    return await create_test_data(datas, CompositionStatus)


async def create_test_types():
    datas = [
        {'name': 'Манга'},
        {'name': 'Манхва'},
        {'name': 'Маньхуа'}
    ]
    return await create_test_data(datas, CompositionType)


async def create_test_genres():
    datas = [
        {'name': 'Боевые искусства'},
        {'name': 'Сёнен'},
        {'name': 'Романтика'},
        {'name': 'Детектив'},
        {'name': 'Сёдзе'}
    ]
    return await create_test_data(datas, CompositionGenre)


async def create_test_tags():
    datas = [
        {'name': 'Веб'},
        {'name': 'ГГ имба'},
        {'name': 'Исекай'},
        {'name': 'Подземелья'},
        {'name': 'Система'},
        {'name': 'Кулинария'},
        {'name': 'Амнезия'}

    ]
    return await create_test_data(datas, CompositionTag)


@pytest.fixture(scope='session')
async def create_test_compositions(

):
    age_ratings_objs = await create_test_age_ratings()
    types_objs = await create_test_types()
    genres_objs = await create_test_genres()
    statuses_objs = await create_test_statuses()
    tags_objs = await create_test_tags()


    dt1 = datetime(2024, 1, 1, hour=0,
                  minute=0, second=0, microsecond=0)
    dt2 = datetime(2024, 2, 22, hour=0,
                   minute=0, second=0, microsecond=0)
    dt3 = datetime(2024, 3, 23, hour=0,
                   minute=0, second=0, microsecond=0)
    dt4 = datetime(2024, 4, 12, hour=0,
                   minute=0, second=0, microsecond=0)
    dt5 = datetime(2024, 5, 11, hour=0,
                   minute=0, second=0, microsecond=0)

    datas = [
        {
            'slug': 'testovaya-manga-1',
            'title': 'Тестовая манга 1',
            'english_title': 'Test manga 1',
            'another_name_title': 'another name test manga 1',
            'year_of_creations': 1990,
            'created_at': dt1,
            'updated_at': dt1,
            'descriptions': 'description test manga 1',
            'type': types_objs[1],
            'status': statuses_objs[0],
            'age_rating': age_ratings_objs[1],
            'composition_genres': [
                genres_objs[0],
                genres_objs[1]
            ],
            'composition_tags': [
                tags_objs[0],
                tags_objs[1],
                tags_objs[4]
            ]
        },
        {
            'slug': 'testovaya-manga-2',
            'title': 'Тестовая манга 2',
            'english_title': 'Test manga 2',
            'another_name_title': 'another name test manga 2',
            'year_of_creations': 1992,
            'created_at': dt2,
            'updated_at': dt2,
            'descriptions': 'description test manga 2',
            'type': types_objs[0],
            'status': statuses_objs[0],
            'age_rating': age_ratings_objs[2],
            'composition_genres': [
                genres_objs[2],
                genres_objs[4]
            ],
            'composition_tags': [
                tags_objs[0],
                tags_objs[6],
            ]
        },
        {
            'slug': 'testovaya-manga-3',
            'title': 'Тестовая манга 3',
            'english_title': 'Test manga 3',
            'another_name_title': 'another name test manga 3',
            'year_of_creations': 2003,
            'created_at': dt3,
            'updated_at': dt3,
            'descriptions': 'description test manga 3',

            'type': types_objs[1],
            'status': statuses_objs[0],
            'age_rating': age_ratings_objs[2],
            'composition_genres': [
                genres_objs[1]
            ],
            'composition_tags': [
                tags_objs[1],
                tags_objs[2],
                tags_objs[3],
                tags_objs[4]
            ]
        },
        {
            'slug': 'testovaya-manga-4',
            'title': 'Тестовая манга 4',
            'english_title': 'Test manga 4',
            'another_name_title': 'another name test manga 4',
            'year_of_creations': 2014,
            'created_at': dt4,
            'updated_at': dt4,
            'descriptions': 'description test manga 4',

            'type': types_objs[0],
            'status': statuses_objs[2],
            'age_rating': age_ratings_objs[0],
            'composition_genres': [
                genres_objs[1],
                genres_objs[3]
            ],
            'composition_tags': [
                tags_objs[1],
            ]
        },
        {
            'slug': 'testovaya-manga-5',
            'title': 'Тестовая манга 5',
            'english_title': 'Test manga 5',
            'another_name_title': 'another name test manga 5',
            'year_of_creations': 2007,
            'created_at': dt5,
            'updated_at': dt5,
            'descriptions': 'description test manga 5',

            'type': types_objs[2],
            'status': statuses_objs[1],
            'age_rating': age_ratings_objs[2],
            'composition_genres': [
                genres_objs[0],
                genres_objs[4]
            ],
            'composition_tags': [
                tags_objs[5],
                tags_objs[0],
            ]
        }
    ]
    await create_test_data(datas, Composition)


