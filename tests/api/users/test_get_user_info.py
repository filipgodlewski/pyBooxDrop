from unittest import mock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from boox.api.core import TokenMissingError
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataUser, UserInfoResponse
from tests.api.users.conftest import FakeUserInfoResponse
from tests.api.utils import E2EConfig
from tests.conftest import e2e

# pyright: reportPrivateUsage=false


def test_get_user_info_calls_get_and_parses_response(
    mocker: MockerFixture,
    fake_user_info_response: FakeUserInfoResponse,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_user_info_response.build().model_dump()
    api = UsersApi(session=mocker.Mock())
    api._get = mocker.Mock(return_value=mocked_response)

    result = api.get_user_info()

    api._get.assert_called_once_with(endpoint="/api/1/users/me")
    assert isinstance(result, UserInfoResponse)
    assert isinstance(result.data, DataUser)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_get_user_info_integration(
    mocker: MockerFixture,
    faker: Faker,
    fake_user_info_response: FakeUserInfoResponse,
    mocked_client: mock.Mock,
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_user_info_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.get.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url, token=faker.uuid4()) as boox:
        result = boox.users.get_user_info()

    mocked_client.get.assert_called_once_with(url.value + "/api/1/users/me")
    mocked_response.json.assert_called_once()
    assert isinstance(result, UserInfoResponse)
    assert isinstance(result.data, DataUser)


def test_get_user_info_raises_token_missing_error(mocked_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mocked_boox.users.get_user_info()


@e2e
def test_get_user_info_e2e(config: E2EConfig):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        response = boox.users.get_user_info()

    assert response.data.area_code
    assert response.data.login_type == "email"
    assert response.data.email == config.email_address
