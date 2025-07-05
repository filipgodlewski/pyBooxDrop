import gc

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from boox.api.users import UsersApi
from boox.client import Boox
from boox.models.enums import BooxUrl
from boox.models.protocols import HttpClient


def shows_all_members(e: ValidationError) -> bool:
    errors = e.errors(include_url=False, include_context=False, include_input=False)
    return all(m.value in errors[0]["msg"] for m in list(BooxUrl))


def test_boox_initializes_with_defaults():
    assert Boox()


def test_boox_base_url_is_none_by_default():
    boox = Boox()
    assert boox.base_url is None


@pytest.mark.parametrize("url", list(BooxUrl))
def test_boox_base_url_inferred_from_client(mocker: MockerFixture, url: BooxUrl):
    mocked_client = mocker.Mock(spec=HttpClient)
    mocked_client.base_url = url
    boox = Boox(client=mocked_client)
    assert boox.base_url is url


def test_boox_raises_validation_error_for_invalid_url(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)
    mocked_client.base_url = "http://random.url"
    with pytest.raises(ValidationError, match="Input should be", check=shows_all_members):
        Boox(client=mocked_client)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_boox_base_url_can_be_set(mocker: MockerFixture, url: BooxUrl):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    boox.base_url = url
    assert boox.base_url is url


def test_boox_base_url_set_raises_on_invalid_url(mocker: MockerFixture):
    mocked_client = mocker.Mock(spec=HttpClient)

    boox = Boox(client=mocked_client)
    with pytest.raises(ValidationError, match="Input should be", check=shows_all_members):
        boox.base_url = "http://random.url"


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
