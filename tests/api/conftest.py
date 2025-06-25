import os

import pytest

from boox.client import BooxClient
from boox.models.base import BooxApiUrl
from boox.models.enums import BooxDomain
from tests.utils import EmailProvider


@pytest.fixture()
def client():
    return BooxClient(url=BooxApiUrl(BooxDomain.EUR))


@pytest.fixture()
def email():
    return EmailProvider()


@pytest.fixture()
def e2e_client():
    domain = BooxDomain(os.environ["E2E_TARGET_DOMAIN"])
    client = BooxClient(url=BooxApiUrl(domain))
    yield client
    client.client.close()
