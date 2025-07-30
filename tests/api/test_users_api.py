import datetime
import re
from unittest import mock
from uuid import uuid1

import pytest
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
)
from tests.api.utils import E2EConfig, EmailProvider
from tests.conftest import e2e

# pyright: reportPrivateUsage=false


def test_boox_client_initializes_users_api(mocked_client: mock.Mock):
    boox = Boox(client=mocked_client)
    assert boox.users._session is boox


def test_send_verification_code_calls_post_and_parses_response(mocker: MockerFixture):
    mocked_session = mocker.Mock()
    api = UsersApi(session=mocked_session)

    mocked_response = mocker.Mock()
    mocked_response.json = mocker.Mock(return_value={"data": "ok", "message": "SUCCESS", "result_code": 0})

    api._post = mocker.Mock(return_value=mocked_response)

    payload = SendVerifyCodeRequest.model_validate({"mobi": "foo@bar.com"})
    result = api.send_verification_code(payload=payload)

    assert result == SendVerifyResponse(data="ok", message="SUCCESS", result_code=0)
    api._post.assert_called_once_with(endpoint="/api/1/users/sendVerifyCode", json={"mobi": "foo@bar.com"})


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_send_verification_code_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {"data": "ok", "message": "SUCCESS", "result_code": 0}
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        payload = SendVerifyCodeRequest.model_validate({"mobi": "foo@bar.com"})
        result = boox.users.send_verification_code(payload=payload)

    expected_url = url.value + "/api/1/users/sendVerifyCode"
    expected_json = payload.model_dump(exclude_unset=True)
    mocked_client.post.assert_called_once_with(expected_url, json=expected_json)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SendVerifyResponse)
    assert result.data == "ok"


def test_fetch_session_token_calls_post_and_parses_response(mocker: MockerFixture):
    token = str(uuid1())
    mocked_session = mocker.Mock()
    api = UsersApi(session=mocked_session)

    mocked_response = mocker.Mock()
    mocked_response.json = mocker.Mock(return_value={"data": {"token": token}, "message": "SUCCESS", "result_code": 0})

    api._post = mocker.Mock(return_value=mocked_response)

    payload = FetchTokenRequest.model_validate({"mobi": "foo@bar.com", "code": "123456"})
    result = api.fetch_session_token(payload=payload)

    data = FetchTokenResponse.model_validate({"data": {"token": token}, "message": "SUCCESS", "result_code": 0})
    assert result == data
    api._post.assert_called_once_with(
        endpoint="/api/1/users/signupByPhoneOrEmail", json={"mobi": "foo@bar.com", "code": "123456"}
    )


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_fetch_session_token_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    token = str(uuid1())
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {"data": {"token": token}, "message": "SUCCESS", "result_code": 0}
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        payload = FetchTokenRequest.model_validate({"mobi": "foo@bar.com", "code": "123456"})
        result = boox.users.fetch_session_token(payload=payload)

    expected_url = url.value + "/api/1/users/signupByPhoneOrEmail"
    expected_json = payload.model_dump(exclude_unset=True)
    mocked_client.post.assert_called_once_with(expected_url, json=expected_json)
    mocked_response.json.assert_called_once()
    assert isinstance(result, FetchTokenResponse)
    data = DataToken.model_validate({"token": token})
    assert result.data == data


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_sync_token_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    token = str(uuid1())
    mocked_response = mocker.Mock()
    data = {
        "channels": (),
        "cookie_name": "foo",
        "expires": datetime.datetime.now(tz=datetime.UTC),
        "session_id": "xyz123",
    }
    mocked_response.json = mocker.Mock(
        return_value={"data": data, "message": "SUCCESS", "result_code": 0, "tokenExpiredAt": 1}
    )
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.get.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url, token=token) as boox:
        result = boox.users.synchronize_session_token()

    expected_url = url.value + "/api/1/users/syncToken"
    mocked_client.get.assert_called_once_with(expected_url)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SyncSessionTokenResponse)
    assert result.data == DataSession.model_validate(data)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_2(mocked_client: mock.Mock, url: BooxUrl):
    with (
        Boox(client=mocked_client, base_url=url) as boox,
        pytest.raises(TokenMissingError, match="Bearer token is required to call this method"),
    ):
        boox.users.synchronize_session_token()


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
def test_synchronize_token_e2e(config: E2EConfig):
    if not config.token:
        pytest.skip("Token was either not obtainer or not set")

    with Boox(base_url=config.domain, token=config.token) as boox:
        response = boox.users.synchronize_session_token()

    assert response.token_expired_at
