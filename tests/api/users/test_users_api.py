from unittest import mock

from boox.core import Boox

# pyright: reportPrivateUsage=false


def test_users_api_has_access_to_boox(mocked_client: mock.Mock):
    boox = Boox(client=mocked_client)
    assert boox.users._session is boox
