import re
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from boox.api.users import UsersApi
from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse
from tests.conftest import e2e
from tests.utils import EmailProvider

# pyright: reportPrivateUsage=false


# Move to test_core
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
    api._post.assert_called_once_with(endpoint="/users/sendVerifyCode", json={"mobi": "foo@bar.com"})


@pytest.mark.parametrize("url", list(BooxUrl))
def test_users_api_send_verification_code_integration(mocker: MockerFixture, mocked_client: mock.Mock, url: BooxUrl):
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {"data": "ok", "message": "SUCCESS", "result_code": 0}
    mocked_response.raise_for_status.return_value = mocked_response
    mocked_client.post.return_value = mocked_response

    with Boox(client=mocked_client, base_url=url) as boox:
        payload = SendVerifyCodeRequest(mobi="foo@bar.com")
        result = boox.users.send_verification_code(payload=payload)

    expected_url = url.value + "users/sendVerifyCode"
    expected_json = payload.model_dump(exclude_unset=True)
    mocked_client.post.assert_called_once_with(expected_url, json=expected_json)
    mocked_response.json.assert_called_once()
    assert isinstance(result, SendVerifyResponse)
    assert result.data == "ok"


@e2e
def test_send_verification_code_e2e(client: Boox, email: EmailProvider):
    payload = SendVerifyCodeRequest(mobi=email.address)

    response = client.users.send_verification_code(payload=payload)
    assert response.data == "ok"
    message = email.get_newest_message()
    match = re.compile(r"^The code is (\d{6}) for account verification from BOOX.").match(message)
    assert match, "Did not match the received email"
