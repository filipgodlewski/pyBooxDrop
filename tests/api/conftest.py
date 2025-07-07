from collections.abc import Iterator
from contextlib import suppress
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from tests.utils import EmailProvider


@pytest.fixture
def mocked_boox(mocker: MockerFixture) -> mock.Mock:
    boox: mock.Mock = mocker.Mock()
    boox.base_url = None
    return boox


@pytest.fixture(scope="session")
def email() -> Iterator[EmailProvider]:
    """An email provider for connecting to an SMTP server.

    Useful for getting the verification code.
    At the end of the session all messages in the inbox are cleaned-up.

    Yields:
        EmailProvider: a testing-only wrapper on httpx.Client.
    """
    with EmailProvider() as provider:
        yield provider
        with suppress(ValueError):
            provider.cleanup_inbox()
