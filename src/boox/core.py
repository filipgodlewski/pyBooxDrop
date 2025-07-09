import warnings

from pydantic import ConfigDict, TypeAdapter, validate_call

from boox.__about__ import __version__
from boox.api.users import UsersApi
from boox.client import BaseHttpClient
from boox.models.enums import BooxUrl
from boox.models.protocols import HttpClient


class Boox:
    """The client used to communicate with the BOOXDrop remote server.

    It is not meant to be used with the local connection (via USB protocol) as it has a completely different API.

    Examples:
        Example 1, using as a context manager.

        >>> # Given it is the very first connection, and no token is available:
        >>> with Boox(base_url="https://eur.boox.com/api/1/") as client:
        ...     payload = {"mobi": "foo@bar.com"}
        ...     client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)

        Example 2, closing the connection manually.
        Notice that you can also use BooxUrl enum to not rely on strings for the base_url

        >>> from boox.models.enums import BooxUrl
        >>> client = Boox(base_url=BooxUrl.EUR)
        >>> payload = {"mobi": "foo@bar.com"}
        >>> client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)
        >>> client.close()
    """

    def __init__(self, client: HttpClient | None = None, base_url: BooxUrl | None = None) -> None:
        if is_closed := getattr(client, "is_closed", False):
            raise ValueError("Cannot initialize Boox with a closed connection")

        if base_url := (getattr(client, "base_url", None) or base_url):
            base_url = TypeAdapter(BooxUrl).validate_python(base_url)

        self._is_closed: bool = is_closed
        self._base_url: str | None = base_url
        self.client: HttpClient = client or BaseHttpClient()
        self.users = UsersApi(self)
        self.client.headers.update({
            "User-Agent": f"python-boox/{__version__}",
            "Content-Type": "application/json",
        })

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        if getattr(self, "is_closed", True) is False:
            warnings.warn(
                "Boox client was not closed explicitly (neither via `with` nor `.close()`)",
                ResourceWarning,
                stacklevel=2,
            )
            self.close()

    @property
    def base_url(self) -> str | None:
        """Property to conveniently store and set the base_url that will be used for API calls.

        Returns:
            str | None: Please refer to `BooxUrl`.
        """
        return self._base_url

    @base_url.setter
    @validate_call(config=ConfigDict(use_enum_values=True))
    def base_url(self, value: BooxUrl):
        self._base_url = value

    @property
    def is_closed(self):
        """Property to check whether a client's connection is closed."""
        return self._is_closed

    def close(self):
        """An explicit way of closing the Boox client."""
        if not self.is_closed and getattr(self, "client", None) is not None:
            self.client.close()
            self._is_closed = True
