from typing import TYPE_CHECKING

import pytest

from boox.api.core import TokenMissingError
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataDevice, DeviceInfoResponse
from tests.api.utils import E2EConfig
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.users.conftest import FakeDeviceInfoResponse

# pyright: reportPrivateUsage=false


def test_get_device_info_parses_response_correctly(
    mocker: "MockerFixture",
    fake_device_info_response: "FakeDeviceInfoResponse",
):
    api = UsersApi(session=mocker.Mock())
    api._get = mocker.Mock(return_value=mocker.Mock(json=fake_device_info_response.build().model_dump))

    result = api.get_device_info()

    api._get.assert_called_once_with(endpoint="/api/1/users/getDevice")
    assert isinstance(result, DeviceInfoResponse)
    assert isinstance(result.data, tuple)
    assert all(isinstance(d, DataDevice) for d in result.data)


def test_get_user_info_raises_token_missing_error(mock_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mock_boox.users.get_device_info()


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_get_device_info_parses_response_correctly(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_device_info_response: "FakeDeviceInfoResponse",
    mock_client: "Mock",
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_device_info_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mock_client.get.return_value = mocked_response

    with Boox(client=mock_client, base_url=url, token=faker.uuid4()) as boox:
        result = boox.users.get_device_info()

    mock_client.get.assert_called_once_with(url.value + "/api/1/users/getDevice")
    mocked_response.json.assert_called_once()
    mocked_response.raise_for_status.assert_called_once()
    assert isinstance(result, DeviceInfoResponse)
    assert isinstance(result.data, tuple)
    assert all(isinstance(d, DataDevice) for d in result.data)


@e2e
def test_get_device_info_e2e(config: "E2EConfig"):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        result = boox.users.get_device_info()

    assert isinstance(result.data, tuple)
    assert all(d.id for d in result.data)
