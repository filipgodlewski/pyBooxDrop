import respx
from httpx import Response

from boox.api.users import UsersApi
from boox.client import BooxClient
from boox.models.base import BooxApiUrl
from boox.models.enums import BooxDomain
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse


def test_boox_client_initializes_users_api():
    url = BooxApiUrl(BooxDomain.EUR)
    client = BooxClient(url=url)

    assert isinstance(client.users, UsersApi)
    assert client.users._session is client  # pyright: ignore[reportPrivateUsage]


def test_send_verification_code():
    payload = SendVerifyCodeRequest(mobi="foo@bar.com")
    response = SendVerifyResponse(data="ok", message="SUCCESS", result_code=0).model_dump_json()

    with respx.mock(base_url="https://eur.boox.com/api/1/") as respx_mock:
        route = respx_mock.post("users/sendVerifyCode").mock(return_value=Response(200, content=response))

        client = BooxClient(url=BooxDomain.EUR)  # pyright: ignore[reportArgumentType]
        result = client.users.send_verification_code(payload=payload)

    assert route.called
    assert isinstance(result, SendVerifyResponse)
    assert result.data == "ok"
    assert str(result) == "<0: SUCCESS>"
