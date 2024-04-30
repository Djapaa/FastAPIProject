from httpx import AsyncClient
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
