import datetime
import json
import uuid

from pydantic import EmailStr
from httpx import AsyncClient
from pytest_mock import MockerFixture

from ...api_v1.auth.services import redis_set_email_verification_key, redis_get_email_by_uuid
from ...api_v1.auth.tasks import send_verification_mail, get_message
from ...api_v1.auth import services
from .fixtures import create_user, create_login_user
import pytest

from ...config.redis_conf import test_redis


async def mock_redis_set_email_verification_key(email: EmailStr, uuid: str):
    await test_redis.set(uuid, email, 10 * 60)


async def mock_redis_get_email_by_uuid(uuid: str):
    return await test_redis.get(uuid)


def mock_send_mail_return(username, email, verify_uuid):
    return True


def mock_get_token():
    return '12345ef'


@pytest.mark.parametrize('data, expected_status, expected_response',
                         [
                             (
                                     {
                                         "username": "test1",
                                         "email": "test1@mail.ru",
                                         "password": "testpassword"
                                     },
                                     201,
                                     {
                                         "id": 2,
                                         "username": "test1",
                                         "email": "test1@mail.ru",
                                         "is_stuff": False,
                                         "is_superuser": False,
                                         "is_verified": False,
                                         "balance": "0",
                                         "descriptions": None,
                                         "gender": "Not specified",
                                         "created_at": datetime.datetime.utcnow(),
                                         "email_not": False,
                                         "avatar": "media/user/default.png"

                                     }
                             ),
                             (
                                     {
                                         "username": "",
                                         "email": "test2@mail.ru",
                                         "password": "testpassword"
                                     },
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "string_too_short",
                                                 "loc": [
                                                     "body",
                                                     "username"
                                                 ],
                                                 "msg": "String should have at least 4 characters",
                                                 "input": "",
                                                 "ctx": {
                                                     "min_length": 4
                                                 },
                                                 "url": "https://errors.pydantic.dev/2.6/v/string_too_short"
                                             }
                                         ]
                                     }

                             ),
                             (
                                     {
                                         "username": "testuser",
                                         "email": "",
                                         "password": "testpassword"
                                     },
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "value_error",
                                                 "loc": [
                                                     "body",
                                                     "email"
                                                 ],
                                                 "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
                                                 "input": "",
                                                 "ctx": {
                                                     "reason": "The email address is not valid. It must have exactly one @-sign."
                                                 }
                                             }
                                         ]
                                     }
                             ),
                             (
                                     {
                                         "username": "testuser",
                                         "email": "test@",
                                         "password": "testpassword"
                                     },
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "value_error",
                                                 "loc": [
                                                     "body",
                                                     "email"
                                                 ],
                                                 "msg": "value is not a valid email address: There must be something after the @-sign.",
                                                 "input": "test@",
                                                 "ctx": {
                                                     "reason": "There must be something after the @-sign."
                                                 }
                                             }
                                         ]
                                     }

                             ),
                             (
                                     {
                                         "username": "testuser",
                                         "email": "test@mail.ru",
                                         "password": ""
                                     },
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "string_too_short",
                                                 "loc": [
                                                     "body",
                                                     "password"
                                                 ],
                                                 "msg": "String should have at least 4 characters",
                                                 "input": "",
                                                 "ctx": {
                                                     "min_length": 4
                                                 },
                                                 "url": "https://errors.pydantic.dev/2.6/v/string_too_short"
                                             }
                                         ]
                                     }

                             ),
                             (
                                     {
                                         "username": "test1111",
                                         "email": "test@mail.ru",
                                         "password": "12345"
                                     },
                                     400,
                                     {
                                         "detail": "User with such email or login already exists"
                                     }

                             ),
                             (
                                     {
                                         "username": "test",
                                         "email": "test11111@mail.ru",
                                         "password": "12345"
                                     },
                                     400,
                                     {
                                         "detail": "User with such email or login already exists"
                                     }

                             )
                         ])
async def test_create_user(
        ac: AsyncClient,
        monkeypatch,
        create_user,
        data: dict,
        expected_status: int,
        expected_response
):
    # мок на отправку сообщения на почту
    monkeypatch.setattr(send_verification_mail, 'delay', mock_send_mail_return)
    # мок на установку ключа верификации в редис
    monkeypatch.setattr(services, 'redis_set_email_verification_key', mock_redis_set_email_verification_key)
    # мок на получение ключа верификации в редис
    monkeypatch.setattr(services, 'redis_get_email_by_uuid', mock_redis_get_email_by_uuid)

    response = await ac.post('/api/v1/auth/signup/', json=data)

    assert response.status_code == expected_status

    verify_uuid = str(uuid.uuid4())
    await redis_set_email_verification_key(data['email'], verify_uuid)
    redis_email = await redis_get_email_by_uuid(verify_uuid)
    # проверка на то, что по установленному uuid: email можно получить email
    assert redis_email == data['email']
    # Проверка на то что функция запускается
    assert send_verification_mail.delay(data['username'], data['email'], verify_uuid) == True

    response_json = response.json()
    if response.status_code == 201:
        assert response_json['id'] == expected_response['id']
        assert response_json['username'] == expected_response['username']
        assert response_json['email'] == expected_response['email']
        assert response_json['is_stuff'] == expected_response['is_stuff']
        assert response_json['is_superuser'] == expected_response['is_superuser']
        assert response_json['is_verified'] == expected_response['is_verified']
        assert response_json['balance'] == expected_response['balance']
        assert response_json['descriptions'] == expected_response['descriptions']
        assert response_json['gender'] == expected_response['gender']
        # assert user['created_at'] == expected_response['created_at']
        assert response_json['email_not'] == expected_response['email_not']
        assert response_json['avatar'] == expected_response['avatar']
    else:
        assert response_json == expected_response


@pytest.mark.parametrize('data, expected_status, expected_response',
                         [
                             (
                                     {
                                         'username': 'test@mail.ru',
                                         'password': '12345'
                                     },
                                     200,
                                     {
                                         'access_token': '12345ef',
                                         'type': 'bearer'
                                     }

                             ),
                             (
                                     {
                                         'username': 'test1111@mail.ru',
                                         'password': '12345'
                                     },
                                     400,
                                     {
                                         "detail": "Incorrect email or password"
                                     }

                             ),
                             (
                                     {
                                         'username': 'test@mail.ru',
                                         'password': '123456'
                                     },
                                     400,
                                     {
                                         "detail": "Incorrect email or password"
                                     }

                             ),
                             (
                                     {
                                         'username': '',
                                         'password': ''
                                     },
                                     422,
                                     {
                                         "detail": [
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "username"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": None,
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             },
                                             {
                                                 "type": "missing",
                                                 "loc": [
                                                     "body",
                                                     "password"
                                                 ],
                                                 "msg": "Field required",
                                                 "input": None,
                                                 "url": "https://errors.pydantic.dev/2.6/v/missing"
                                             }
                                         ]
                                     }

                             )
                         ])
async def test_login(
        ac: AsyncClient,
        create_user,
        monkeypatch,
        data,
        expected_status,
        expected_response
):
    monkeypatch.setattr(services, 'get_token', mock_get_token)

    response = await ac.post('/api/v1/auth/login/', data=data)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize('headers, expected_status, expected_response',
                         [
                             (
                                     {'Authorization': 'Bearer 1q2w3e'},
                                     200,
                                     {
                                         'id': 1,
                                         'username': 'test',
                                         'email': 'test@mail.ru',
                                         'is_stuff': False,
                                         'is_superuser': False,
                                         'is_verified': True,
                                         'balance': "0.00",
                                         'descriptions': None,
                                         'gender': 'Not specified',
                                         'created_at': '2024-01-01T00:00:00',
                                         'email_not': False,
                                         'avatar': 'media/user/default.png'
                                     }
                             ),
                             (
                                     {'Authorization': 'Bearer 1q2w3eeee'},
                                     401,
                                     {
                                         "detail": "Invalid authentication credentials"
                                     }
                             ),
                             (
                                     {},
                                     401,
                                     {
                                         "detail": "Not authenticated"
                                     }
                             )

                         ])
async def test_current_user(
        ac: AsyncClient,
        create_login_user,
        headers,
        expected_status,
        expected_response
):
    response = await ac.get('/api/v1/auth/current/', headers=headers)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize('headers, expected_status, expected_response',
                         [
                             (
                                     {},
                                     401,
                                     {
                                         "detail": "Not authenticated"
                                     }
                             ),

                             (
                                     {'Authorization': 'Bearer 1q2w3ee'},
                                     401,
                                     {
                                         "detail": "Invalid authentication credentials"
                                     }
                             ),

                             (
                                     {'Authorization': 'Bearer 1q2w3e'},
                                     204,
                                     {}
                             )
                         ])
async def test_logout(
        ac: AsyncClient,
        create_login_user,
        headers,
        expected_status,
        expected_response
):
    response = await ac.post('/api/v1/auth/logout/', headers=headers)
    assert response.status_code == expected_status
    if response.status_code != 204:
        assert response.json() == expected_response
