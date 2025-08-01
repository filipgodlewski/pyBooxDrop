from http import HTTPStatus
from http.client import HTTPMessage
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING
from urllib.error import HTTPError

import pytest

from boox.client import BaseHttpClient, BaseHTTPError, BaseHttpResponse

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from tests.conftest import ExpectedResponseData

SUCCESSES = (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT)
FAILURES = (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND, HTTPStatus.INTERNAL_SERVER_ERROR)

# pyright: reportPrivateUsage=false


def assert_response(actual: BaseHttpResponse, expected_data: "ExpectedResponseData"):
    assert isinstance(actual, BaseHttpResponse)
    assert actual._code == expected_data.code
    assert actual._url == expected_data.url
    assert actual._headers == expected_data.headers
    assert actual._content == expected_data.content


@pytest.mark.parametrize("code", FAILURES)
def test_http_error_str_includes_code_and_phrase(code: HTTPStatus):
    error = BaseHTTPError.__new__(BaseHTTPError)
    error.code = code
    assert str(error) == f"HTTP Error {code.value}: {code.phrase}"


@pytest.mark.parametrize("code", FAILURES)
def test_http_error_repr_includes_code_and_phrase(code: HTTPStatus):
    error = BaseHTTPError.__new__(BaseHTTPError)
    error.code = code
    assert repr(error) == f"<HTTP Error {code.value}: {code.phrase!r}>"


def test_http_error_content_decodes_empty_bytes():
    error = BaseHTTPError.__new__(BaseHTTPError)
    error._content = b''
    assert not error.content


def test_http_error_url_is_settable():
    error = BaseHTTPError.__new__(BaseHTTPError)
    error.url = (url := "https://foo.bar")
    assert error.url == url


def test_http_error_headers_are_settable():
    error = BaseHTTPError.__new__(BaseHTTPError)
    error.headers = {"foo": "bar"}
    assert error.headers == {"foo": "bar"}


def test_base_http_client_has_empty_headers():
    client = BaseHttpClient()
    assert client.headers == {}


def test_base_http_client_can_be_closed():
    client = BaseHttpClient()
    client.close()


def test_build_request_with_json_payload():
    client = BaseHttpClient()
    client.headers = {"X": "Y"}
    request = client._build_request(method="POST", url="https://foo.com", json={"foo": "bar"})
    assert request.get_full_url() == "https://foo.com"
    assert request.data == b'{"foo": "bar"}'
    assert request.get_header("X") == "Y"
    assert request.get_method() == "POST"


def test_request_error_is_caught_and_can_be_raised_for_status(mocker: "MockerFixture"):
    client = BaseHttpClient()
    headers = HTTPMessage()
    headers.add_header("X", "Y")
    http_error = HTTPError(code=500, url="https://foo.com", msg="Internal Server Error", hdrs=headers, fp=None)

    mocker.patch("boox.client.urlopen").side_effect = http_error
    response = client._send(request=mocker.Mock())
    with pytest.raises(BaseHTTPError) as e:
        response.raise_for_status()

    assert e.value.url == "https://foo.com"
    assert e.value.code is HTTPStatus.INTERNAL_SERVER_ERROR
    assert e.value.headers == {"X": "Y"}


def test_send_populates_response_fields_correctly(mocker: "MockerFixture", mocked_urlopen: "ExpectedResponseData"):
    client = BaseHttpClient()
    response = client._send(request=mocker.Mock())
    assert_response(response, mocked_urlopen)


def test_get_populates_response_fields_correctly(mocker: "MockerFixture", mocked_urlopen: "ExpectedResponseData"):
    client = BaseHttpClient()
    spy = mocker.spy(client, "_build_request")
    response = client.get(mocked_urlopen.url)

    spy.assert_called_once_with("GET", mocked_urlopen.url, None)
    assert_response(response, mocked_urlopen)


def test_post_populates_response_fields_correctly(mocker: "MockerFixture", mocked_urlopen: "ExpectedResponseData"):
    client = BaseHttpClient()
    spy = mocker.spy(client, "_build_request")
    payload = loads(mocked_urlopen.content)
    response = client.post(mocked_urlopen.url, payload)

    spy.assert_called_once_with("POST", mocked_urlopen.url, payload)
    assert_response(response, mocked_urlopen)


def test_delete_populates_response_fields_correctly(mocker: "MockerFixture", mocked_urlopen: "ExpectedResponseData"):
    client = BaseHttpClient()
    spy = mocker.spy(client, "_build_request")
    response = client.delete(mocked_urlopen.url)

    spy.assert_called_once_with("DELETE", mocked_urlopen.url, None)
    assert_response(response, mocked_urlopen)


@pytest.mark.parametrize("code", SUCCESSES)
def test_base_http_response_repr_returns_status_code(code: HTTPStatus):
    response = BaseHttpResponse.__new__(BaseHttpResponse)
    response._code = code

    assert repr(response) == f"<Response [{code.value}]>"


@pytest.mark.parametrize("code", SUCCESSES)
def test_raise_for_status_returns_response_on_success(code: HTTPStatus):
    response = BaseHttpResponse.__new__(BaseHttpResponse)
    response._code = code

    assert response.raise_for_status() is response


@pytest.mark.parametrize("code", FAILURES)
def test_raise_for_status_raises_on_failure(code: HTTPStatus):
    response = BaseHttpResponse(code=code, url="foo.com", headers={}, content=b"")

    with pytest.raises(BaseHTTPError):
        response.raise_for_status()


def test_response_json_parses_empty_object():
    response = BaseHttpResponse.__new__(BaseHttpResponse)
    response._content = b'{}'

    assert response.json() == {}


def test_response_json_raises_on_invalid_json():
    response = BaseHttpResponse.__new__(BaseHttpResponse)
    response._content = b''

    with pytest.raises(JSONDecodeError):
        response.json()
