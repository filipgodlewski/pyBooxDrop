import pytest

from boox.client import BooxClient
from boox.models.base import BooxApiUrl
from boox.models.enums import BooxDomain


@pytest.fixture()
def client():
    return BooxClient(url=BooxApiUrl(BooxDomain.EUR))
