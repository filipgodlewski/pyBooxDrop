from unittest import mock
from uuid import uuid1

import pytest
from pytest_mock import MockerFixture

from boox.api.core import TokenMissingError
from boox.core import Boox
from boox.models.config_users import SyncTokenResponse
from boox.models.enums import BooxUrl
from tests.api.utils import E2EConfig
from tests.conftest import e2e


@pytest.mark.parametrize("url", list(BooxUrl))
def test_sync_token_raises_token_missing_error(mocked_client: mock.Mock, url: BooxUrl):
    with (
        Boox(client=mocked_client, base_url=url) as boox,
        pytest.raises(TokenMissingError, match="Bearer token is required to call this method"),
    ):
        boox.config_users.synchronize_token()


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_sync_token_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    token = str(uuid1())
    mocked_response = mocker.Mock()
    mocked_response.json = mocker.Mock(
        return_value={"data": None, "message": "SUCCESS", "result_code": 0, "tokenExpiredAt": 1}
    )
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
def test_synchronize_token_e2e(config: E2EConfig):
    if not config.token:
        pytest.skip("Token was either not obtainer or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        response = boox.config_users.synchronize_token()

    assert not response.data
    assert response.token_expired_at
