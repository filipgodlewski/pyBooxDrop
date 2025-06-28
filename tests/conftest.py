import os
from typing import TYPE_CHECKING

import pytest

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
