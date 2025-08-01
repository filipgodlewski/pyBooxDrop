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


def test_sync_token_raises_token_missing_error(mocked_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mocked_boox.config_users.synchronize_token()


@pytest.mark.parametrize("url", list(BooxUrl))
def test_config_users_api_sync_token_integration(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_sync_token_response: "FakeSyncTokenResponse",
    mocked_client: "Mock",
    url: BooxUrl,
):
    token = faker.uuid4()
    return_value = fake_sync_token_response.build()
    mocked_response = mocker.Mock()
    mocked_response.json = mocker.Mock(return_value=return_value.model_dump())
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.get.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url, token=token) as boox:
        result = boox.config_users.synchronize_token()

    expected_url = url.value + "/api/1/configUsers/one"
    mocked_client.get.assert_called_once_with(expected_url)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SyncTokenResponse)
    assert not result.data


@e2e
def test_synchronize_token_e2e(config: "E2EConfig"):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        response = boox.config_users.synchronize_token()

    assert not response.data
    assert response.token_expired_at
