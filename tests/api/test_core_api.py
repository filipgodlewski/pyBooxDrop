from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from boox.api.core import Api, TokenMissingError, requires_token
from boox.client import BaseHTTPError
from boox.core import Boox
from boox.models.enums import BooxUrl

if TYPE_CHECKING:
    from unittest.mock import Mock

    from faker import Faker
    from pytest_mock import MockerFixture

# pyright: reportPrivateUsage=false


class DummyApi(Api):
    @requires_token
    def dummy_method(self):
        return self


def test_api_cannot_be_instantiated_directly(mocker: "MockerFixture"):
    with pytest.raises(TypeError, match=r"Cannot instantiate abstract class Api directly"):
        Api(session=mocker.Mock())


def test_prepare_url_raises_without_base_url(mocker: "MockerFixture"):
    mock_session = mocker.Mock()
    mock_session.base_url = None
    api = DummyApi(session=mock_session)
    with pytest.raises(ValueError, match=r"base_url must be filled"):
        api._prepare_url("/endpoint")


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_joins_base_and_endpoint_without_leading_slash(mocker: "MockerFixture", url: BooxUrl):
    mock_session = mocker.Mock()
    mock_session.base_url = url
    api = DummyApi(session=mock_session)

    endpoint = "endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}/{endpoint}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_joins_base_and_endpoint_with_leading_slash(mocker: "MockerFixture", url: BooxUrl):
    mock_session = mocker.Mock()
    mock_session.base_url = url
    api = DummyApi(session=mock_session)
    endpoint = "/endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_strips_trailing_slash(mocker: "MockerFixture", url: BooxUrl):
    mock_session = mocker.Mock()
    mock_session.base_url = url + "/"
    api = DummyApi(session=mock_session)
    endpoint = "/endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint}"


def test_post_calls_client_and_checks_status(mocker: "MockerFixture"):
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(return_value=mocked_response)

    mock_client = mocker.Mock()
    mock_client.post = mocker.Mock(return_value=mocked_response)

    mock_session = mocker.Mock()
    mock_session.client = mock_client

    api = DummyApi(session=mock_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value="https://foo.com/endpoint")

    result = api._post(endpoint="/endpoint", json={"foo": "bar"})

    api._prepare_url.assert_called_once_with("/endpoint")
    mock_client.post.assert_called_once_with("https://foo.com/endpoint", json={"foo": "bar"})
    mocked_response.raise_for_status.assert_called_once()
    assert result == mocked_response


def test_post_raises_on_http_error(mocker: "MockerFixture"):
    url = "https://foo.com/endpoint"
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(side_effect=BaseHTTPError(url, HTTPStatus.BAD_REQUEST, {}, b''))

    mock_client = mocker.Mock()
    mock_client.post = mocker.Mock(return_value=mocked_response)

    mock_session = mocker.Mock()
    mock_session.client = mock_client

    api = DummyApi(session=mock_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value=url)

    with pytest.raises(BaseHTTPError):
        api._post(endpoint="/endpoint")


def test_method_raises_error_for_missing_token(mock_client: "Mock"):
    mock_session = Boox(client=mock_client)

    api = DummyApi(session=mock_session)

    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        api.dummy_method()


def test_method_succeeds_with_token(faker: "Faker", mock_client: "Mock"):
    mock_session = Boox(client=mock_client)
    mock_session.token = faker.uuid4()

    api = DummyApi(session=mock_session)

    assert api.dummy_method()


def test_get_calls_client_and_checks_status(mocker: "MockerFixture"):
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(return_value=mocked_response)

    mock_client = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=mocked_response)

    mock_session = mocker.Mock()
    mock_session.client = mock_client

    api = DummyApi(session=mock_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value="https://foo.com/endpoint")

    result = api._get(endpoint="/endpoint")

    api._prepare_url.assert_called_once_with("/endpoint")
    mock_client.get.assert_called_once_with("https://foo.com/endpoint")
    mocked_response.raise_for_status.assert_called_once()
    assert result == mocked_response
