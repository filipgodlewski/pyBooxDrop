import re
import warnings

import httpx
from pydantic import SecretStr, validate_call

from boox.api.users import UsersApi
from boox.models.base import BooxApiUrl


class Boox:
    """The client used to communicate with the BOOXDrop remote server.

    It is not meant to be used with the local connection (via USB protocol) as it has a completely different API.

    Note that this class is in fact a context manager. It is highly recommended to use it as such.
    If you prefer to not use it as a context manager, please remember to **close the connection** manually.

    Examples:
        Example 1, using as a context manager. Note that you must initialize the Boox class every time
        you start a context manager. This is due to the fact, that it relies on httpx library.
        httpx library, upon leaving the context manager, terminates the connection.

        >>> # Given it is the very first connection, and no token is available:
        >>> with Boox(url="eur.boox.com") as client:
        ...     payload = {"mobi": "foo@bar.com"}
        ...     client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)

        Example 2, closing the connection manually. It is not recommended, but it's not my job to stop you from that.

        >>> client = Boox(url="eur.boox.com")
        >>> payload = {"mobi": "foo@bar.com"}
        >>> client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)
        >>> client.close()
    """

    @validate_call()
    def __init__(self, *, base_url: BooxApiUrl, token: SecretStr | None = None) -> None:
        self.client = httpx.Client(base_url=str(base_url))
        self.token: SecretStr = token or SecretStr("")
        self.users = UsersApi(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} on {self.client.base_url!s}"

    def __repr__(self) -> str:
        host = self.client.base_url.host
        path = self.client.base_url.path
        match = re.compile(r"\d+").search(path)
        if not match:
            raise ValueError("No api version found in the base url!")

        api_version = match.group()
        has_token = bool(self.token)
        return f"{self.__class__.__name__}({host=}, {api_version=}, {has_token=})"

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        if not self.client.is_closed:
            warnings.warn("Boox was not closed explicitly", ResourceWarning, stacklevel=2)
            self.close()

    def close(self):
        if not self.client.is_closed:
            self.client.close()
