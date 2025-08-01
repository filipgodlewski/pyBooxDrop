import pytest

from tests.api.utils import E2EConfig


@pytest.fixture(scope="session")
def config() -> E2EConfig:
    return E2EConfig()
