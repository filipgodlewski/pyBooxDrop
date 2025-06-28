import re

import respx

from boox.api.users import UsersApi
from boox.client import BooxClient
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse
from tests.conftest import e2e
from tests.utils import EmailProvider


def test_boox_client_initializes_users_api(client: BooxClient):
    assert isinstance(client.users, UsersApi)
    assert client.users._session is client  # pyright: ignore[reportPrivateUsage]


@respx.mock(assert_all_called=True, assert_all_mocked=True, base_url="https://eur.boox.com/api/1/")
def test_send_verification_code(respx_mock: respx.MockRouter, client: BooxClient):
    response = SendVerifyResponse(data="ok", message="SUCCESS", result_code=0).model_dump()
    route = respx_mock.post("users/sendVerifyCode").respond(json=response)

    payload = SendVerifyCodeRequest(mobi="foo@bar.com")
    result = client.users.send_verification_code(payload=payload)

    assert route.called
    assert isinstance(result, SendVerifyResponse)
    assert result.data == "ok"
    assert str(result) == "<0: SUCCESS>"


@e2e
def test_send_verification_code_e2e(client: BooxClient, email: EmailProvider):
    payload = SendVerifyCodeRequest(mobi=email.address)

    response = client.users.send_verification_code(payload=payload)
    assert response.data == "ok"
    message = email.get_verification_code()
    match = re.compile(r"^The code is (\d{6}) for account verification from BOOX.").match(message)
    assert match, "Did not match the received email"
