from typing import TYPE_CHECKING

import pytest

from boox.api.core import TokenMissingError
from boox.core import Boox
from boox.models.config_users import SyncTokenResponse
from boox.models.enums import BooxUrl
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.config_users.conftest import FakeSyncTokenResponse
    from tests.api.utils import E2EConfig


def test_sync_token_raises_token_missing_error(mock_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mock_boox.config_users.synchronize_token()


@pytest.mark.parametrize("url", list(BooxUrl))
def test_config_users_api_sync_token_parses_response_correctly(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_sync_token_response: "FakeSyncTokenResponse",
    mock_client: "Mock",
    url: BooxUrl,
):
    token = faker.uuid4()
    return_value = fake_sync_token_response.build()
    mock_response = mocker.Mock()
    mock_response.json = mocker.Mock(return_value=return_value.model_dump())
    mock_response.raise_for_status.return_value = mock_response
    mock_client.get.return_value = mock_response

    with Boox(client=mock_client, base_url=url, token=token) as boox:
        result = boox.config_users.synchronize_token()

    expected_url = url.value + "/api/1/configUsers/one"
    mock_client.get.assert_called_once_with(expected_url)
    mock_response.json.assert_called_once()
    assert isinstance(result, SyncTokenResponse)
    assert not result.data


@e2e
def test_synchronize_token_e2e(config: "E2EConfig"):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        result = boox.config_users.synchronize_token()

    assert not result.data
    assert result.token_expired_at
