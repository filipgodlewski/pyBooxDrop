from typing import TYPE_CHECKING

import pytest

from boox.api.core import TokenMissingError
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataUser, UserInfoResponse
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.users.conftest import FakeUserInfoResponse
    from tests.api.utils import E2EConfig

# pyright: reportPrivateUsage=false


def test_get_user_info_calls_get_and_parses_response(
    mocker: "MockerFixture",
    fake_user_info_response: "FakeUserInfoResponse",
):
    api = UsersApi(session=mocker.Mock())
    api._get = mocker.Mock(return_value=mocker.Mock(json=fake_user_info_response.build().model_dump))

    result = api.get_user_info()

    api._get.assert_called_once_with(endpoint="/api/1/users/me")
    assert isinstance(result, UserInfoResponse)
    assert isinstance(result.data, DataUser)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_get_user_info_parses_response_correctly(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_user_info_response: "FakeUserInfoResponse",
    mock_client: "Mock",
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_user_info_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mock_client.get.return_value = mocked_response

    with Boox(client=mock_client, base_url=url, token=faker.uuid4()) as boox:
        result = boox.users.get_user_info()

    mock_client.get.assert_called_once_with(url.value + "/api/1/users/me")
    mocked_response.json.assert_called_once()
    mocked_response.raise_for_status.assert_called_once()
    assert isinstance(result, UserInfoResponse)
    assert isinstance(result.data, DataUser)


def test_get_user_info_raises_token_missing_error(mocked_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mocked_boox.users.get_user_info()


@e2e
def test_get_user_info_e2e(config: "E2EConfig"):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        result = boox.users.get_user_info()

    assert result.data.area_code
    assert result.data.login_type == "email"
    assert result.data.email == config.email_address
