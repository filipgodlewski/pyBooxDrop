from typing import TYPE_CHECKING

import pytest

from boox.api.core import TokenMissingError
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataSession, SyncSessionTokenResponse
from tests.api.utils import E2EConfig
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.users.conftest import FakeSyncSessionTokenResponse

# pyright: reportPrivateUsage=false


def test_sync_session_token_calls_get_and_parses_response(
    mocker: "MockerFixture",
    fake_sync_session_token_response: "FakeSyncSessionTokenResponse",
):
    api = UsersApi(session=mocker.Mock())
    api._get = mocker.Mock(return_value=mocker.Mock(json=fake_sync_session_token_response.build().model_dump))

    result = api.synchronize_session_token()

    api._get.assert_called_once_with(endpoint="/api/1/users/syncToken")
    assert isinstance(result, SyncSessionTokenResponse)
    assert isinstance(result.data, DataSession)


def test_sync_session_token_raises_token_missing_error(mocked_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mocked_boox.users.synchronize_session_token()


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_sync_session_token_integration(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_sync_session_token_response: "FakeSyncSessionTokenResponse",
    mocked_client: "Mock",
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_sync_session_token_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.get.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url, token=faker.uuid4()) as boox:
        result = boox.users.synchronize_session_token()

    mocked_client.get.assert_called_once_with(url.value + "/api/1/users/syncToken")
    mocked_response.json.assert_called_once()
    mocked_response.raise_for_status.assert_called_once()
    assert isinstance(result, SyncSessionTokenResponse)
    assert isinstance(result.data, DataSession)


@e2e
def test_synchronize_session_token_e2e(config: E2EConfig):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        result = boox.users.synchronize_session_token()

    assert result.data.expires
