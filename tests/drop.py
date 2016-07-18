import pytest
import requests


@pytest.fixture
def drop(drop_url):
    return drop_url + 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopo'


@pytest.fixture
def post_headers():
    return {
        'Content-Type': 'application/octet-stream',
        'Authorization': 'Client Qabel',
    }


def test_is_up(drop_url):
    response = requests.get(drop_url)
    assert response.status_code == 404


def test_create_drop(drop, post_headers):
    print(drop)
    response = requests.post(drop, data=b'1234', headers=post_headers)
    assert response.status_code == 200
    assert response.content == b''
    response = requests.get(drop)
    assert b'1234' in response.content
