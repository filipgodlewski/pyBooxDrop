import os
from collections.abc import Iterator
from contextlib import suppress

import pytest

from tests.utils import EmailProvider


@pytest.fixture(scope="session")
def e2e_doamin() -> str:
    return os.environ["E2E_TARGET_DOMAIN"]


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
