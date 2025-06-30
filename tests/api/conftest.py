import os
from collections.abc import Iterator
from contextlib import suppress

import pytest
from _pytest.fixtures import SubRequest

from boox.client import Boox
from boox.models.enums import BooxUrl
from tests.utils import EmailProvider


@pytest.fixture(scope="session")
def client(request: SubRequest) -> Iterator[Boox]:
    """A client used for mocked and E2E tests.

    Used as a context manager to utilize the keep-alive functionality.

    Yields:
        Iterator[Boox]: A client that can be used for api testing.
    """

    domain = os.environ["E2E_TARGET_DOMAIN"] if request.config.getoption("--e2e") else BooxUrl.EUR
    with Boox(base_url=BooxUrl(domain)) as client:
        yield client


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
