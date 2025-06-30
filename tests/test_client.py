import uuid

import pytest
from pydantic import ValidationError

from boox.client import Boox
from boox.models.enums import BooxUrl


def test_invalid_boox_domain_is_not_allowed():
    with pytest.raises(ValidationError) as err:
        Boox(base_url="https://foo.com")  # pyright: ignore[reportArgumentType]
    assert all(m.value in str(err) for m in BooxUrl)


@pytest.mark.parametrize("url", list(BooxUrl))
def test_valid_boox_domain_as_string_is_allowed(url: BooxUrl):
    client = Boox(base_url=url)  # pyright: ignore[reportArgumentType]
    assert client.base_url == url


@pytest.mark.parametrize("url", list(BooxUrl))
def test_client_str_representation(url: BooxUrl):
    client = Boox(base_url=url)
    assert str(client) == f"BooxDrop through {url}"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_client_repr_without_token(url: BooxUrl):
    client = Boox(base_url=url)
    assert repr(client) == f"Boox(url={url.value}, has_token=False)"


@pytest.mark.parametrize("url", list(BooxUrl))
def test_client_repr_with_token(url: BooxUrl):
    token = uuid.uuid1()
    client = Boox(base_url=url, token=str(token))  # pyright: ignore[reportArgumentType]
    assert repr(client) == f"Boox(url={url.value}, has_token=True)"
