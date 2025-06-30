import uuid

import pytest
from pydantic import ValidationError

from boox.client import Boox
from boox.models.enums import BooxUrl


def test_invalid_boox_domain_is_not_allowed():
    def shows_all_members(e: ValidationError) -> bool:
        errors = e.errors(include_url=False, include_context=False, include_input=False)
        return all(m.value in errors[0]["msg"] for m in list(BooxUrl))

    with pytest.raises(ValidationError, match=r"Input should be", check=shows_all_members):
        Boox(base_url="https://foo.com")  # pyright: ignore[reportArgumentType]


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
