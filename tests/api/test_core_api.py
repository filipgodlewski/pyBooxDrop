from http import HTTPStatus
from unittest import mock
from uuid import uuid1

import pytest
from pytest_mock import MockerFixture

from boox.api.core import Api, TokenMissingError, requires_token
from boox.client import BaseHTTPError
from boox.core import Boox
from boox.models.enums import BooxUrl

# pyright: reportPrivateUsage=false


class DummyApi(Api):
    @requires_token
    def dummy_method(self):
        return self


def test_api_cannot_be_instantiated_directly(mocker: MockerFixture):
    with pytest.raises(TypeError, match=r"Cannot instantiate abstract class Api directly"):
        Api(session=mocker.Mock())


def test_prepare_url_raises_without_base_url(mocker: MockerFixture):
    mocked_session = mocker.Mock()
    mocked_session.base_url = None
    api = DummyApi(session=mocked_session)
    with pytest.raises(ValueError, match=r"base_url must be filled"):
        api._prepare_url("/endpoint")


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_joins_base_and_endpoint_without_leading_slash(mocker: MockerFixture, url: BooxUrl):
    mocked_session = mocker.Mock()
    mocked_session.base_url = url
    api = DummyApi(session=mocked_session)

    endpoint = "endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}/{endpoint}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_joins_base_and_endpoint_with_leading_slash(mocker: MockerFixture, url: BooxUrl):
    mocked_session = mocker.Mock()
    mocked_session.base_url = url
    api = DummyApi(session=mocked_session)
    endpoint = "/endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_strips_trailing_slash(mocker: MockerFixture, url: BooxUrl):
    mocked_session = mocker.Mock()
    mocked_session.base_url = url + "/"
    api = DummyApi(session=mocked_session)
    endpoint = "/endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint}"


def test_post_calls_client_and_checks_status(mocker: MockerFixture):
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(return_value=mocked_response)

    mocked_client = mocker.Mock()
    mocked_client.post = mocker.Mock(return_value=mocked_response)

    mocked_session = mocker.Mock()
    mocked_session.client = mocked_client

    api = DummyApi(session=mocked_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value="https://foo.com/endpoint")

    result = api._post(endpoint="/endpoint", json={"foo": "bar"})

    api._prepare_url.assert_called_once_with("/endpoint")
    mocked_client.post.assert_called_once_with("https://foo.com/endpoint", json={"foo": "bar"})
    mocked_response.raise_for_status.assert_called_once()
    assert result == mocked_response


def test_post_raises_on_http_error(mocker: MockerFixture):
    url = "https://foo.com/endpoint"
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(side_effect=BaseHTTPError(url, HTTPStatus.BAD_REQUEST, {}, b''))

    mocked_client = mocker.Mock()
    mocked_client.post = mocker.Mock(return_value=mocked_response)

    mocked_session = mocker.Mock()
    mocked_session.client = mocked_client

    api = DummyApi(session=mocked_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value=url)

    with pytest.raises(BaseHTTPError):
        api._post(endpoint="/endpoint")


def test_method_raises_error_for_missing_token(mocked_client: mock.Mock):
    mocked_session = Boox(client=mocked_client)

    api = DummyApi(session=mocked_session)

    with pytest.raises(TokenMissingError, match="Bearer token is required to call this method"):
        api.dummy_method()


def test_method_succeeds_with_token(mocked_client: mock.Mock):
    mocked_session = Boox(client=mocked_client)
    mocked_session.token = str(uuid1())

    api = DummyApi(session=mocked_session)

    assert api.dummy_method()


def test_get_calls_client_and_checks_status(mocker: MockerFixture):
    mocked_response = mocker.Mock()
    mocked_response.raise_for_status = mocker.Mock(return_value=mocked_response)

    mocked_client = mocker.Mock()
    mocked_client.get = mocker.Mock(return_value=mocked_response)

    mocked_session = mocker.Mock()
    mocked_session.client = mocked_client

    api = DummyApi(session=mocked_session)
    api._prepare_url = mocker.patch.object(api, "_prepare_url", return_value="https://foo.com/endpoint")

    result = api._get(endpoint="/endpoint")

    api._prepare_url.assert_called_once_with("/endpoint")
    mocked_client.get.assert_called_once_with("https://foo.com/endpoint")
    mocked_response.raise_for_status.assert_called_once()
    assert result == mocked_response
