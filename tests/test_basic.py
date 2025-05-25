from boox.client import Client


def test_client_import_and_init(client: Client):
    assert client.authorize() == client.token
