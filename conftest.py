
import pytest


@pytest.fixture
def accounting_url(request):
    return request.config.getoption('accounting_url')


@pytest.fixture
def accounting_user(request):
    return {
        'username': 'testuser',
        'password': 'testuser',
    }


@pytest.fixture
def block_url(request):
    return request.config.getoption('block_url')


@pytest.fixture
def drop_url(request):
    return request.config.getoption('drop_url')


@pytest.fixture
def index_url(request):
    return request.config.getoption('index_url')


def pytest_addoption(parser):
    parser.addoption('--accounting-url',
                     default='http://localhost:9696/',
                     help='URL of the accounting server')
    parser.addoption('--block-url',
                     default='http://localhost:9697/',
                     help='URL of the block server')
    parser.addoption('--drop-url',
                     default='http://localhost:5000/',
                     help='URL of the drop server')
    parser.addoption('--index-url',
                     default='http://localhost:9698/',
                     help='URL of the index server')
