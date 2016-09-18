
import pytest
import requests

from .accounting import fresh_accounting_token


@pytest.fixture
def search_url(index_url):
    return index_url + 'api/v0/search?email=foo@example.net'


def test_is_up(index_url):
    response = requests.get(index_url)
    assert response.status_code == 404


def test_authorization(search_url, fresh_accounting_token):
    response = requests.get(search_url, headers={
        'Authorization': 'Token ' + fresh_accounting_token,
    })
    assert response.status_code == 200
    json = response.json()
    assert not json['identities']


def test_missing_authorization(search_url):
    response = requests.get(search_url)
    assert response.status_code == 403
    json = response.json()
    assert 'identities' not in json


def test_wrong_authorization(search_url):
    response = requests.get(search_url, headers={
        'Authorization': 'Token Asdf',
    })
    assert response.status_code == 403
    json = response.json()
    assert 'identities' not in json
