from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from boox.core import Boox

# pyright: reportPrivateUsage=false


def test_users_api_has_access_to_boox(mocked_boox: "Boox"):
    assert mocked_boox.users._session is mocked_boox
