from unittest import mock

import pytest

from boox.api.core import Api
from boox.models.enums import BooxUrl

# pyright: reportPrivateUsage=false


class DummyApi(Api):
    pass


def test_api_cannot_be_instantiated_directly(mocked_boox: mock.Mock):
    with pytest.raises(TypeError, match=r"Cannot instantiate abstract class Api directly"):
        Api(session=mocked_boox)


def test_prepare_url_raises_without_base_url(mocked_boox: mock.Mock):
    api = DummyApi(session=mocked_boox)
    with pytest.raises(ValueError, match=r"base_url must be filled"):
        api._prepare_url("/endpoint")


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_joins_base_and_endpoint(mocked_boox: mock.Mock, url: BooxUrl):
    mocked_boox.base_url = url
    api = DummyApi(session=mocked_boox)

    endpoint = "endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_prepare_url_strips_leading_slash(mocked_boox: mock.Mock, url: BooxUrl):
    mocked_boox.base_url = url
    api = DummyApi(session=mocked_boox)
    endpoint = "/endpoint"
    assert api._prepare_url(endpoint) == f"{url.value}{endpoint.lstrip("/")}"


def test_a(mocked_boox: mock.Mock):
    DummyApi(session=mocked_boox)
    # TODO: Mock client.post respone (ok)
    # TODO: Check that returns response


def test_b(mocked_boox: mock.Mock):
    DummyApi(session=mocked_boox)
    # TODO: Mock client.post respone (error)
    # TODO: Check that raises HTTPError
