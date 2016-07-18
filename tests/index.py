
import requests


def test_is_up(index_url):
    response = requests.get(index_url)
    assert response.status_code == 404
