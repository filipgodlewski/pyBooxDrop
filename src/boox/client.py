import httpx
from pydantic import SecretStr, validate_call

from boox.api.users import UsersApi
from boox.models.base import BooxApiUrl


class BooxClient:
    """The client used to communicate with the BOOXDrop remote server.

    It is not meant to be used with the local connection (via USB protocol) as it has a completely different API.

    Example usages:
        >>> # Given it is the very first connection, and no token is available:
        >>> client = BooxClient(url="eur.boox.com")
        >>> payload = {"mobi": "foo@bar.com"}
        >>> client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)
    """

    @validate_call()
    def __init__(self, *, url: BooxApiUrl, token: SecretStr | None = None) -> None:
        self.client = httpx.Client(base_url=str(url))
        self.token: SecretStr = token or SecretStr("")
        self.users = UsersApi(self)
