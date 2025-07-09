import os
from http import HTTPStatus
from typing import TYPE_CHECKING, NamedTuple
from unittest import mock

import pytest
from pytest_mock import MockerFixture

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.nodes import Item

e2e = pytest.mark.e2e


def pytest_addoption(parser: "Parser"):
    parser.addoption("--e2e", action="store_true", default=False, help="run end-to-end tests")


def pytest_collection_modifyitems(config: "Config", items: list["Item"]) -> None:
    if config.getoption("--e2e"):
        required_env_variables = ["E2E_SMTP_EMAIL", "E2E_SMTP_X_API_KEY", "E2E_TARGET_DOMAIN"]
        if missing := [v for v in required_env_variables if not os.getenv(v)]:
            pytest.exit(f"Missing required environment variables for --e2e: {", ".join(missing)}")
        return

    skip_e2e = pytest.mark.skip(reason="use --e2e to run end-to-end tests")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture
def mocked_client(mocker: MockerFixture) -> mock.Mock:
    client: mock.Mock = mocker.Mock()
    client.is_closed = False
    client.base_url = None
    client.headers = {}
    return client


class ExpectedResponseData(NamedTuple):
    code: HTTPStatus
    url: str
    headers: dict[str, str]
    content: bytes


@pytest.fixture
def mocked_urlopen(mocker: MockerFixture) -> ExpectedResponseData:
    data = ExpectedResponseData(HTTPStatus.OK, "https://foo.com/", {"X": "Y"}, b'{"foo": "bar"}')
    mocked_response = mocker.Mock()
    mocked_response.status = data.code
    mocked_response.geturl.return_value = data.url
    mocked_response.headers = data.headers
    mocked_response.read.return_value = data.content
    mocker.patch("boox.client.urlopen").return_value.__enter__.return_value = mocked_response
    return data
