from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from boox.core import Boox

# pyright: reportPrivateUsage=false


def test_users_api_has_access_to_boox(mock_boox: "Boox"):
    assert mock_boox.users._session is mock_boox
