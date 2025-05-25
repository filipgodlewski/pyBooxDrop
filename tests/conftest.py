import pytest

from boox.client import Client


@pytest.fixture(scope="session")
def client():
    return Client(token="dummy-token")
