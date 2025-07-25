import re
from unittest import mock
from uuid import uuid1

import pytest
from pytest_mock import MockerFixture

from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import (
    DataToken,
    FetchTokenRequest,
    FetchTokenResponse,
    SendVerifyCodeRequest,
    SendVerifyResponse,
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

    payload = SendVerifyCodeRequest(mobi="foo@bar.com")
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
        payload = SendVerifyCodeRequest(mobi="foo@bar.com")
        result = boox.users.send_verification_code(payload=payload)

    expected_url = url.value + "/api/1/users/sendVerifyCode"
    expected_json = payload.model_dump(exclude_unset=True)
    mocked_client.post.assert_called_once_with(expected_url, json=expected_json)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SendVerifyResponse)
    assert result.data == "ok"


def test_fetch_session_token_calls_post_and_parses_response(mocker: MockerFixture):
    token = uuid1()
    mocked_session = mocker.Mock()
    api = UsersApi(session=mocked_session)

    mocked_response = mocker.Mock()
    mocked_response.json = mocker.Mock(
        return_value={"data": {"token": str(token)}, "message": "SUCCESS", "result_code": 0}
    )

    api._post = mocker.Mock(return_value=mocked_response)

    payload = FetchTokenRequest(mobi="foo@bar.com", code="123456")
    result = api.fetch_session_token(payload=payload)

    data = FetchTokenResponse.model_validate({"data": {"token": str(token)}, "message": "SUCCESS", "result_code": 0})
    assert result == data
    api._post.assert_called_once_with(
        endpoint="/api/1/users/signupByPhoneOrEmail", json={"mobi": "foo@bar.com", "code": "123456"}
    )


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_fetch_session_token_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    token = uuid1()
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {"data": {"token": str(token)}, "message": "SUCCESS", "result_code": 0}
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        payload = FetchTokenRequest(mobi="foo@bar.com", code="123456")
        result = boox.users.fetch_session_token(payload=payload)

    expected_url = url.value + "/api/1/users/signupByPhoneOrEmail"
    expected_json = payload.model_dump(exclude_unset=True)
    mocked_client.post.assert_called_once_with(expected_url, json=expected_json)
    mocked_response.json.assert_called_once()
    assert isinstance(result, FetchTokenResponse)
    data = DataToken.model_validate({"token": str(token)})
    assert result.data == data


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

    with Boox(base_url=config.domain, token=config.token.get_secret_value()) as boox:
        response = boox.users.synchronize_token()

    assert response.token_expired_at
