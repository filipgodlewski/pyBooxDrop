from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from boox.core import Boox
from boox.models.enums import BooxUrl
from tests.api.utils import E2EConfig

if TYPE_CHECKING:
    from unittest.mock import Mock


@pytest.fixture(scope="session")
def config() -> E2EConfig:
    return E2EConfig()


@pytest.fixture
def mock_boox(mock_client: "Mock") -> Iterator[Boox]:
    with Boox(client=mock_client, base_url=BooxUrl.EUR) as boox:
        yield boox
