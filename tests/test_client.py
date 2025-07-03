import gc

import httpx
import pytest
import requests
from pytest_mock import MockerFixture

from boox.api.users import UsersApi
from boox.client import Boox
from boox.models.protocols import HttpClient


def test_boox_is_not_closed_after_init(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    assert boox.is_closed is False


def test_boox_is_closed_after_context_exit(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    with (boox := Boox(client=mocked_client)):
        pass
    assert boox.is_closed


def test_boox_client_exposed_in_context(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    with Boox(client=mocked_client) as boox:
        assert boox.client is mocked_client


def test_boox_warns_if_not_closed(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    del boox
    with pytest.warns(ResourceWarning, match="Boox client was not closed explicitly"):
        gc.collect()


def test_boox_close_calls_internal_method(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)
    boox = Boox(client=mocked_client)
    mock_close = mocker.patch.object(boox, "close")

    boox.close()
    mock_close.assert_called_once()


def test_boox_raises_on_closed_client(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)
    mocked_client.is_closed = True

    with pytest.raises(ValueError, match="Cannot initialize Boox with a client which has a closed connection"):
        Boox(client=mocked_client)


def test_boox_client_is_assigned_properly(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    assert boox.client is mocked_client


def test_boox_users_api_is_initialized(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    assert isinstance(boox.users, UsersApi)


def test_httpx_client_can_be_used_as_boox_client():
    """An integration test simply checking if httpx.Client can be used as a param."""
    with (boox := Boox(client=(real_client := httpx.Client()))):
        pass
    assert boox.is_closed
    assert real_client.is_closed


# TODO: test Client(base_url=...)


def test_requests_session_can_be_used_as_boox_client():
    """An integration test simply checking if requests.Session can be used as a param.

    Notice that requests.Session() doesn't have `.is_closed` attribute.
    """
    with (boox := Boox(client=requests.Session())):
        pass
    assert boox.is_closed
