from httpx import AsyncClient
from ..test_auth.fixtures import create_user_and_login_token, create_verify_user, create_admin_user_and_login_token, \
    create_admin_user
from .fixtures import create_test_compositions
import pytest


@pytest.mark.parametrize('composition_id, expected_status, expected_response',
                         [
                             (
                                     1,
                                     200,
                                     {'slug': 'testovaya-manga-1', 'title': 'Тестовая манга 1',
                                      'composition_image': 'media/composition/default.png',
                                      'type': {'id': 2, 'name': 'Манхва'}, 'avg_rating': '0.0',
                                      'english_title': 'Test manga 1',
                                      'another_name_title': 'another name test manga 1', 'year_of_creations': 1990,
                                      'descriptions': 'description test manga 1',
                                      'status': {'id': 1, 'name': 'Продолжается'},
                                      'age_rating': {'id': 2, 'name': '18+'},
                                      'composition_genres': [{'id': 1, 'name': 'Боевые искусства'},
                                                             {'id': 2, 'name': 'Сёнен'}],
                                      'composition_tags': [{'id': 1, 'name': 'Веб'},
                                                           {'id': 2, 'name': 'ГГ имба'},
                                                           {'id': 5, 'name': 'Система'}],
                                      'view': 0,
                                      'count_rating': 0,
                                      'count_bookmarks': 0, 'total_votes': 0}

                             ),
                             (
                                     6,
                                     400,
                                     {
                                         "detail": "Composition not found"
                                     },
                             )
                         ])
async def test_get_composition(
        ac: AsyncClient,
        create_test_compositions,
        composition_id,
        expected_status,
        expected_response
):
    path = f'/api/v1/composition/{composition_id}/'
    response = await ac.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize('path, expected_status, expected_response',
                         [
                             (
                                     'api/v1/composition/search/',
                                     200,
                                     [
                                         {'slug': 'testovaya-manga-5',
                                          'title': 'Тестовая манга 5',
                                          'composition_image': 'media/composition/default.png',
                                          'type': {
                                              'id': 3,
                                              'name': 'Маньхуа'
                                          },
                                          'avg_rating': '0.0'
                                          },
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (  # Проверка пагинатора page=1 и order by
                                     'api/v1/composition/search/?page=1&page_size=3&order_by=-created_at',
                                     200,
                                     [
                                         {'slug': 'testovaya-manga-5',
                                          'title': 'Тестовая манга 5',
                                          'composition_image': 'media/composition/default.png',
                                          'type': {
                                              'id': 3,
                                              'name': 'Маньхуа'
                                          },
                                          'avg_rating': '0.0'
                                          },
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }]
                             ),
                             (  # Проверка пагинатора page=2 и order by
                                     'api/v1/composition/search/?page=2&page_size=3&order_by=-created_at',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (  # Проверка пагинатора page=3 и order by
                                     'api/v1/composition/search/?page=3&page_size=3&order_by=-created_at',
                                     200,
                                     []
                             ),
                             (
                                     # проверка year_of_creations__gte
                                     'api/v1/composition/search/?year_of_creations__gte=2000',
                                     200,
                                     [
                                         {'slug': 'testovaya-manga-5',
                                          'title': 'Тестовая манга 5',
                                          'composition_image': 'media/composition/default.png',
                                          'type': {
                                              'id': 3,
                                              'name': 'Маньхуа'
                                          },
                                          'avg_rating': '0.0'
                                          },
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка year_of_creations__lte
                                     'api/v1/composition/search/?year_of_creations__lte=2000',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка year_of_creations__lte и year_of_creations__gte
                                     'api/v1/composition/search/?year_of_creations__gte=2000&year_of_creations__lte=2004',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка types__id__in
                                     'api/v1/composition/search/?types__id__in=1,2',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка types__id__in типа произведения которого нет
                                     'api/v1/composition/search/?types__id__in=444',
                                     200,
                                     []
                             ),
                             (
                                     # проверка statuses__id__in
                                     'api/v1/composition/search/?statuses__id__in=1',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка statuses__id__in типа произведения которого нет
                                     'api/v1/composition/search/?statuses__id__in=444',
                                     200,
                                     []
                             ),
                             (
                                     # проверка age_ratings__id__in
                                     'api/v1/composition/search/?age_ratings__id__in=2',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка age_ratings__id__in типа произведения которого нет
                                     'api/v1/composition/search/?age_ratings__id__in=444',
                                     200,
                                     []
                             ),
                             (
                                     # проверка genres__id__in
                                     'api/v1/composition/search/?genres__id__in=2,3',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-2',
                                             'title': 'Тестовая манга 2',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка genres__id__in типа произведения которого нет
                                     'api/v1/composition/search/?genres__id__in=444',
                                     200,
                                     []
                             ),
                             (
                                     # проверка tags__id__in
                                     'api/v1/composition/search/?tags__id__in=2',
                                     200,
                                     [
                                         {
                                             'slug': 'testovaya-manga-4',
                                             'title': 'Тестовая манга 4',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 1,
                                                 'name': 'Манга'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-3',
                                             'title': 'Тестовая манга 3',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         },
                                         {
                                             'slug': 'testovaya-manga-1',
                                             'title': 'Тестовая манга 1',
                                             'composition_image': 'media/composition/default.png',
                                             'type': {
                                                 'id': 2,
                                                 'name': 'Манхва'
                                             },
                                             'avg_rating': '0.0'
                                         }
                                     ]
                             ),
                             (
                                     # проверка tags__id__in типа произведения которого нет
                                     'api/v1/composition/search/?tags__id__in=444',
                                     200,
                                     []
                             ),

                         ])
async def test_composition_search(
        ac: AsyncClient,
        create_test_compositions,
        path,
        expected_status,
        expected_response
):
    response = await ac.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize('data, headers, expected_status, expected_response',
                         [
                             # Проверка на то, что обычный пользователь не может создавать произведения
                             (
                                     {
                                         "title": "Тестовая манга 123",
                                         "english_title": "Test manga 123",
                                         "another_name_title": "123 manga Test",
                                         "year_of_creations": 2001,
                                         "descriptions": "Test manga 123 description",
                                         "status": 1,
                                         "type": 0,
                                         "age_rating": 1,
                                         "genres": [
                                             1, 2, 3
                                         ],
                                         "tags": [
                                             3, 4, 5
                                         ]
                                     },
                                     {'Authorization': 'Bearer 1q2w3e'},
                                     403,
                                     {'detail': "Don't have permissions"}
                             ),
                             # Проверка на то, что пользователь с полем is_stuff=True может создавать произведения
                             (
                                     {
                                         "title": "Тестовая манга 123",
                                         "english_title": "Test manga 123",
                                         "another_name_title": "123 manga Test",
                                         "year_of_creations": 2001,
                                         "descriptions": "Test manga 123 description",
                                         "status": 1,
                                         "type": 1,
                                         "age_rating": 1,
                                         "genres": [
                                             1, 2, 3
                                         ],
                                         "tags": [
                                             3, 4, 5
                                         ]
                                     },
                                     {'Authorization': 'Bearer admin_token'},
                                     201,
                                     {
                                         "created": True,
                                         "id": 6
                                     }
                             ),
                             (  # Проверка на то, что неавторизованный пользователь не может создавать произведения
                                     {
                                         "title": "Тестовая манга 123",
                                         "english_title": "Test manga 123",
                                         "another_name_title": "123 manga Test",
                                         "year_of_creations": 2001,
                                         "descriptions": "Test manga 123 description",
                                         "status": 1,
                                         "type": 0,
                                         "age_rating": 1,
                                         "genres": [
                                             1, 2, 3
                                         ],
                                         "tags": [
                                             3, 4, 5
                                         ]
                                     },
                                     {},
                                     401,
                                     {'detail': 'Not authenticated'}
                             ),
                             (
                                     # Проверка на то что поля обязательны для заполнения
                                     {},
                                     {'Authorization': 'Bearer admin_token'},
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "title"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "english_title"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "another_name_title"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "year_of_creations"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "descriptions"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "status"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "type"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "age_rating"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "genres"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "tags"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": {},
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             }
                                         ]
                                     }
                             ),
                             (
                                     # Проверка на то что title не может быть меньше 4 символов а год создания меньше 1980
                                     {
                                         "title": "123",
                                         "english_title": "Test manga 123",
                                         "another_name_title": "123 manga Test",
                                         "year_of_creations": 1979,
                                         "descriptions": "Test manga 123 description",
                                         "status": 1,
                                         "type": 0,
                                         "age_rating": 1,
                                         "genres": [
                                             1, 2, 3
                                         ],
                                         "tags": [
                                             3, 4, 5
                                         ]
                                     },
                                     {'Authorization': 'Bearer admin_token'},
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "string_too_short",
                                                 "loc": [
                                                     "body",
                                                     "title"
                                                 ],
                                                 "msg": "String should have at least 4 characters",
                                                 "input": "123",
                                                 "ctx": {
                                                     "min_length": 4
                                                 },
                                                 "url": "https://errors.pydantic.dev/2.6/v/string_too_short"
                                             },
                                             {
                                                 "type": "greater_than_equal",
                                                 "loc": [
                                                     "body",
                                                     "year_of_creations"
                                                 ],
                                                 "msg": "Input should be greater than or equal to 1980",
                                                 "input": 1979,
                                                 "ctx": {
                                                     "ge": 1980
                                                 },
                                                 "url": "https://errors.pydantic.dev/2.6/v/greater_than_equal"
                                             }
                                         ]
                                     }
                             )

                         ])
async def test_composition_create(
        ac: AsyncClient,
        create_test_compositions,
        create_user_and_login_token,
        create_admin_user_and_login_token,
        data,
        headers,
        expected_status,
        expected_response,

):
    response = await ac.post('/api/v1/composition/', json=data, headers=headers)
    assert response.status_code == expected_status
    assert response.json() == expected_response
