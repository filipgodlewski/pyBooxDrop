from collections.abc import Iterator
from contextlib import suppress
from unittest import mock

import pytest

from tests.api.utils import E2EConfig, EmailProvider


@pytest.fixture(scope="session")
def config() -> E2EConfig:
    return E2EConfig()


@pytest.fixture(scope="session")
def email(config: E2EConfig) -> Iterator[EmailProvider]:
    """An email provider for connecting to an SMTP server.

    Useful for getting the verification code.
    At the end of the session all messages in the inbox are cleaned-up.

    Yields:
        EmailProvider: a testing-only wrapper on httpx.Client.
    """
    provider = EmailProvider(config)
    yield provider
    with suppress(ValueError):
        provider.cleanup_inbox()


@pytest.fixture
def mocked_boox(mocked_client: mock.Mock) -> Iterator[Boox]:
    with Boox(client=mocked_client, base_url=BooxUrl.EUR) as boox:
        yield boox
