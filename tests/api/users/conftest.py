from collections.abc import Iterator
from contextlib import suppress
from unittest import mock

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import FetchTokenResponse, SendVerifyResponse, SyncSessionTokenResponse, UserInfoResponse
from tests.api.utils import E2EConfig, EmailProvider


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


@register_fixture
class FakeSendVerifyResponse(ModelFactory[SendVerifyResponse]):
    __check_model__ = True  # TODO: Remove when `polyfactory` lib is updated to v3


@register_fixture
class FakeFetchTokenResponse(ModelFactory[FetchTokenResponse]):
    __check_model__ = True


@register_fixture
class FakeSyncSessionTokenResponse(ModelFactory[SyncSessionTokenResponse]):
    __check_model__ = True


@register_fixture
class FakeUserInfoResponse(ModelFactory[UserInfoResponse]):
    __check_model__ = True


@pytest.fixture
def mocked_boox(mocked_client: mock.Mock) -> Iterator[Boox]:
    with Boox(client=mocked_client, base_url=BooxUrl.EUR) as boox:
        yield boox
