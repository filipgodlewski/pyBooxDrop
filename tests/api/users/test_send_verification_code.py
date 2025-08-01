import re
from unittest import mock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse
from tests.api.conftest import FakeSendVerifyResponse
from tests.api.utils import E2EConfig, EmailProvider
from tests.conftest import e2e

# pyright: reportPrivateUsage=false


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
