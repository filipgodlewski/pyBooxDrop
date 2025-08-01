import re
from unittest import mock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from boox.api.core import TokenMissingError
from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import (
    DataSession,
    DataToken,
    FetchTokenRequest,
    FetchTokenResponse,
    SendVerifyCodeRequest,
    SendVerifyResponse,
    SyncSessionTokenResponse,
from tests.api.conftest import (
    FakeFetchTokenResponse,
    FakeSendVerifyResponse,
    FakeSyncSessionTokenResponse,
    FakeUserInfoResponse,
)
from tests.api.utils import E2EConfig, EmailProvider
from tests.conftest import e2e

# pyright: reportPrivateUsage=false


def test_boox_client_initializes_users_api(mocked_client: mock.Mock):
    boox = Boox(client=mocked_client)
    assert boox.users._session is boox


def test_send_verification_code_calls_post_and_parses_response(
    mocker: MockerFixture,
    faker: Faker,
    send_verify_response: FakeSendVerifyResponse,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = send_verify_response.build().model_dump()
    api = UsersApi(session=mocker.Mock())
    api._post = mocker.Mock(return_value=mocked_response)

    send_data = {"mobi": faker.email()}
    result = api.send_verification_code(payload=SendVerifyCodeRequest.model_validate(send_data))

    assert isinstance(result, SendVerifyResponse)
    api._post.assert_called_once_with(endpoint="/api/1/users/sendVerifyCode", json=send_data)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_send_verification_code_integration(
    mocker: MockerFixture,
    faker: Faker,
    send_verify_response: FakeSendVerifyResponse,
    mocked_client: mock.Mock,
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = send_verify_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        send_data = {"mobi": faker.email()}
        payload = SendVerifyCodeRequest.model_validate(send_data)
        result = boox.users.send_verification_code(payload=payload)

    mocked_client.post.assert_called_once_with(url.value + "/api/1/users/sendVerifyCode", json=send_data)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SendVerifyResponse)


def test_fetch_session_token_calls_post_and_parses_response(
    mocker: MockerFixture,
    faker: Faker,
    fetch_token_response: FakeFetchTokenResponse,
):
    return_value = fetch_token_response.build()
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = return_value.model_dump()
    api = UsersApi(session=mocker.Mock())
    api._post = mocker.Mock(return_value=mocked_response)

    send_data = {"mobi": faker.email(), "code": str(faker.random_number(digits=6))}
    payload = FetchTokenRequest.model_validate(send_data)
    result = api.fetch_session_token(payload=payload)

    assert result == return_value
    api._post.assert_called_once_with(endpoint="/api/1/users/signupByPhoneOrEmail", json=send_data)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_fetch_session_token_integration(
    mocker: MockerFixture,
    faker: Faker,
    fetch_token_response: FakeFetchTokenResponse,
    mocked_client: mock.Mock,
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fetch_token_response.build().model_dump()
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


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_sync_session_token_integration(
    mocker: MockerFixture,
    faker: Faker,
    sync_session_token_response: FakeSyncSessionTokenResponse,
    mocked_client: mock.Mock,
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = sync_session_token_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.get.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url, token=faker.uuid4()) as boox:
        result = boox.users.synchronize_session_token()

    mocked_client.get.assert_called_once_with(url.value + "/api/1/users/syncToken")
    mocked_response.json.assert_called_once()
    assert isinstance(result, SyncSessionTokenResponse)
    assert isinstance(result.data, DataSession)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_sync_session_token_raises_token_missing_error(mocked_boox: Boox):
    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        mocked_boox.users.synchronize_session_token()


@e2e
@pytest.mark.order(0)
def test_send_verification_code_e2e(config: E2EConfig, email: EmailProvider):
    payload = SendVerifyCodeRequest.model_validate({"mobi": config.email_address})

    with Boox(base_url=config.domain) as boox:
        response = boox.users.send_verification_code(payload=payload)

    assert response.data == "ok"
    message = email.get_newest_message()
    match = re.compile(r"^The code is (?P<code>\d{6}) for account verification from BOOX\.").match(message)
    assert match, "Did not match the received email"
    config.verification_code = match.group("code")


@e2e
@pytest.mark.order(1)
def test_fetch_session_token_e2e(config: E2EConfig):
    if not config.verification_code:
        pytest.skip("Verification code was either not obtained or not set")
    payload = FetchTokenRequest.model_validate({"mobi": config.email_address, "code": config.verification_code})

    with Boox(base_url=config.domain) as boox:
        response = boox.users.fetch_session_token(payload=payload)

    assert response.data.token
    config.token = response.data.token


@e2e
def test_synchronize_session_token_e2e(config: E2EConfig):
    if not config.token:
        pytest.skip("Token was either not obtained or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        response = boox.users.synchronize_session_token()

    assert response.data.expires
