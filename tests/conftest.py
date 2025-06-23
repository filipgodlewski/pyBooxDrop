import pytest

from boox.client import BooxClient
from boox.models.enums import BooxDomain


@pytest.fixture(scope="session")
def client_without_token():
    return BooxClient(url=BooxDomain.EUR)
