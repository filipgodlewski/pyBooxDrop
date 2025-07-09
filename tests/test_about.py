import tomllib
from pathlib import Path
from typing import Any

import pytest

from boox import __about__


@pytest.fixture(scope="session")
def meta() -> dict[str, Any]:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as file:
        data = tomllib.load(file)
    return data["project"]


def test_version_matches_about_metadata(meta: dict[str, Any]):
    assert meta["version"] == __about__.__version__, "versions are out of sync"


def test_name_matches_about_metadata(meta: dict[str, Any]):
    assert meta["name"] == __about__.__title__, "package name is out of sync"


def test_description_matches_about_metadata(meta: dict[str, Any]):
    assert meta["description"] == __about__.__description__, "package description is out of sync"
