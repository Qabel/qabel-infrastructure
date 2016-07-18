
import random

import pytest

import requests


def login(accounting_url, user):
    response = requests.post(accounting_url + 'api/v0/auth/login/', data=user)
    assert response.status_code == 200
    response = requests.post(accounting_url + 'api/v0/auth/login/', json=user)
    assert response.status_code == 200
    return response.json()['key']


def register(accounting_url, username=None):
    if not username:
        username = 'testuser-%d' % random.randrange(2**32)
    password = 'VeryHighEntropyPassphraseFactory'
    response = requests.post(accounting_url + 'api/v0/auth/registration/', json={
        'username': username,
        'email': username + '@example.net',
        'password1': password,
        'password2': password,
    })
    assert response.status_code == 201
    token = response.json()['key']
    login_token = login(accounting_url, {
        'username': username,
        'password': password,
    })
    assert token == login_token
    return token


@pytest.fixture
def accounting_token(accounting_url, accounting_user):
    return login(accounting_url, accounting_user)


@pytest.fixture
def fresh_accounting_token(accounting_url):
    return register(accounting_url)


@pytest.fixture
def authorization_header(accounting_token):
    return {
        'Authorization': 'Token ' + accounting_token,
    }


def test_is_up(accounting_url):
    response = requests.get(accounting_url)
    assert response.status_code == 404


def test_testuser_login(accounting_token):
    assert accounting_token
