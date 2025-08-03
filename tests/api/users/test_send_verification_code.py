import re
from typing import TYPE_CHECKING

import pytest

from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse
from tests.conftest import e2e

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

    from tests.api.users.conftest import FakeSendVerifyResponse
    from tests.api.utils import E2EConfig, EmailProvider

# pyright: reportPrivateUsage=false


def test_send_verification_code_calls_post_and_parses_response(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_send_verify_response: "FakeSendVerifyResponse",
):
    api = UsersApi(session=mocker.Mock())
    api._post = mocker.Mock(return_value=mocker.Mock(json=fake_send_verify_response.build().model_dump))

    send_data = {"mobi": faker.email()}
    result = api.send_verification_code(payload=SendVerifyCodeRequest.model_validate(send_data))

    assert isinstance(result, SendVerifyResponse)
    api._post.assert_called_once_with(endpoint="/api/1/users/sendVerifyCode", json=send_data)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_send_verification_code_parses_response_correctly(
    mocker: "MockerFixture",
    faker: "Faker",
    fake_send_verify_response: "FakeSendVerifyResponse",
    mock_client: "Mock",
    url: BooxUrl,
):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = fake_send_verify_response.build().model_dump()
    mocked_response.raise_for_status.return_value = mocked_response
    mock_client.post.return_value = mocked_response

    with Boox(client=mock_client, base_url=url) as boox:
        send_data = {"mobi": faker.email()}
        payload = SendVerifyCodeRequest.model_validate(send_data)
        result = boox.users.send_verification_code(payload=payload)

    mock_client.post.assert_called_once_with(url.value + "/api/1/users/sendVerifyCode", json=send_data)
    mocked_response.json.assert_called_once()
    mocked_response.raise_for_status.assert_called_once()
    assert isinstance(result, SendVerifyResponse)


@e2e
@pytest.mark.order(0)
def test_send_verification_code_e2e(config: "E2EConfig", email: "EmailProvider"):
    payload = SendVerifyCodeRequest.model_validate({"mobi": config.email_address})

    with Boox(base_url=config.domain) as boox:
        result = boox.users.send_verification_code(payload=payload)

    assert result.data == "ok"
    message = email.get_newest_message()
    match = re.compile(r"^The code is (?P<code>\d{6}) for account verification from BOOX\.").match(message)
    assert match, "Did not match the received email"
    config.verification_code = match.group("code")
