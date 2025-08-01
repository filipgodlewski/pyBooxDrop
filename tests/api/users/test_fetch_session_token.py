from typing import TYPE_CHECKING

import pytest

from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataToken, FetchTokenRequest, FetchTokenResponse
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.users.conftest import FakeFetchTokenResponse
    from tests.api.utils import E2EConfig

# pyright: reportPrivateUsage=false


def test_fetch_session_token_calls_post_and_parses_response(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_fetch_token_response: "FakeFetchTokenResponse",
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_fetch_token_response.build().model_dump()
    api = UsersApi(session=mocker.Mock())
    api._post = mocker.Mock(return_value=mocked_response)

    send_data = {"mobi": faker.email(), "code": str(faker.random_number(digits=6))}
    result = api.fetch_session_token(payload=FetchTokenRequest.model_validate(send_data))

    assert isinstance(result, FetchTokenResponse)
    api._post.assert_called_once_with(endpoint="/api/1/users/signupByPhoneOrEmail", json=send_data)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_fetch_session_token_integration(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_fetch_token_response: "FakeFetchTokenResponse",
    mocked_client: "Mock",
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_fetch_token_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        send_data = {"mobi": faker.email(), "code": str(faker.random_number(digits=6))}
        payload = FetchTokenRequest.model_validate(send_data)
        result = boox.users.fetch_session_token(payload=payload)

    mocked_client.post.assert_called_once_with(url.value + "/api/1/users/signupByPhoneOrEmail", json=send_data)
    mocked_response.json.assert_called_once()
    assert isinstance(result, FetchTokenResponse)
    assert isinstance(result.data, DataToken)


@e2e
@pytest.mark.order(1)
def test_fetch_session_token_e2e(config: "E2EConfig"):
    if not config.verification_code:
        pytest.skip("Verification code was either not obtained or not set")
    payload = FetchTokenRequest.model_validate({"mobi": config.email_address, "code": config.verification_code})

    with Boox(base_url=config.domain) as boox:
        response = boox.users.fetch_session_token(payload=payload)

    assert response.data.token
    config.token = response.data.token
