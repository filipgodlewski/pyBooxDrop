from collections.abc import Iterator
from unittest import mock

import pytest

from boox.core import Boox
from boox.models.enums import BooxUrl
from tests.api.utils import E2EConfig


@pytest.fixture(scope="session")
def config() -> E2EConfig:
    return E2EConfig()


@pytest.fixture
def mocked_boox(mocked_client: mock.Mock) -> Iterator[Boox]:
    with Boox(client=mocked_client, base_url=BooxUrl.EUR) as boox:
        yield boox
