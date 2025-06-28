import pytest
from httpx import URL
from pydantic import ValidationError

from boox.client import BooxClient
from boox.models.enums import BooxDomain


def test_invalid_boox_domain_is_not_allowed():
    with pytest.raises(ValidationError) as err:
        BooxClient(url="https://foo.com")  # pyright: ignore[reportArgumentType]
    assert all(m.value in str(err) for m in BooxDomain)


@pytest.mark.parametrize("url", [m.value for m in BooxDomain])
def test_valid_boox_domain_as_string_is_allowed(url: str):
    client = BooxClient(url=url)  # pyright: ignore[reportArgumentType]
    expected_url = URL(f"https://{url}/api/1/")
    assert client.client.base_url == expected_url
