
import pytest
import requests

from .accounting import authorization_header, accounting_token, fresh_accounting_token


@pytest.fixture
def block_prefix(block_url, authorization_header):
    response = requests.post(block_url + 'api/v0/prefix/', headers=authorization_header)
    assert response.status_code == 201
    return response.json()['prefix']


def upload(block_url, headers, path, data):
    url = block_url + 'api/v0/files/' + path
    response = requests.post(url, headers=headers, data=data)
    assert response.status_code == 204
    return url, response.headers['ETag']


def test_is_up(block_url):
    response = requests.get(block_url)
    assert response.status_code == 404


def test_upload_round_trip(block_url, block_prefix, authorization_header):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    url, etag = upload(block_url, authorization_header, path, data)
    response = requests.get(url)
    assert response.headers['ETag']
    assert response.content == data

    response = requests.get(url, headers={'If-None-Match': etag})
    assert response.status_code == 304  # not modified

    new_data = b'some other data'
    url, new_etag = upload(block_url, authorization_header, path, new_data)
    assert new_etag != etag

    response = requests.get(url, headers={'If-None-Match': etag})
    assert response.status_code == 200
    assert response.content == new_data


def test_upload_etag(block_url, block_prefix, authorization_header):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    url, etag = upload(block_url, authorization_header, path, data)

    # POST with ETag
    new_data = b'1234'
    post_header = dict(authorization_header)
    post_header['If-Match'] = etag
    upload(block_url, post_header, path, new_data)

    # POST with ETag but outdated ETag
    response = requests.post(url, headers=post_header, data=new_data)
    assert response.status_code == 412


def test_upload_unauthorized(block_url, block_prefix, authorization_header):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    authorization_header['Authorization'] += '1234'
    with pytest.raises(AssertionError):
        upload(block_url, authorization_header, path, data)


def test_delete(block_url, block_prefix, authorization_header):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    url, etag = upload(block_url, authorization_header, path, data)

    response = requests.delete(url, headers=authorization_header)
    assert response.status_code == 204

    response = requests.get(url)
    assert response.status_code == 404

    response = requests.get(url, headers={'ETag': etag})
    assert response.status_code == 404


def test_delete_unauthorized(block_url, block_prefix, authorization_header):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    url, etag = upload(block_url, authorization_header, path, data)

    authorization_header['Authorization'] += '1234'
    response = requests.delete(url, headers=authorization_header)
    assert response.status_code == 403


def test_delete_unauthorized_wrong_user(block_url, block_prefix, authorization_header, fresh_accounting_token):
    path = block_prefix + '/1234'
    data = b'Yay 12345'

    url, etag = upload(block_url, authorization_header, path, data)

    response = requests.delete(url, headers={
        'Authorization': 'Token ' + fresh_accounting_token,
    })
    assert response.status_code == 403
