import os
from collections.abc import Iterator
from contextlib import suppress

import pytest

from boox.core import Boox
from boox.models.enums import BooxUrl
from tests.utils import EmailProvider


@pytest.fixture
def client() -> Iterator[Boox]:
    """A simple client used for E2E tests.

    Yields:
        Iterator[Boox]: A client that can be used for api testing.
    """
    with Boox(base_url=BooxUrl(os.environ["E2E_TARGET_DOMAIN"])) as boox:
        yield boox


@pytest.fixture(scope="session")
def email() -> Iterator[EmailProvider]:
    """An email provider for connecting to an SMTP server.

    Useful for getting the verification code.
    At the end of the session all messages in the inbox are cleaned-up.

    Yields:
        EmailProvider: a testing-only wrapper on httpx.Client.
    """
    provider = EmailProvider()
    yield provider
    with suppress(ValueError):
        provider.cleanup_inbox()
