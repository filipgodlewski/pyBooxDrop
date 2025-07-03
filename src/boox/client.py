import warnings

from pydantic import ConfigDict, validate_call

from boox.api.users import UsersApi
from boox.models.protocols import HttpClient


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
        >>> with Boox(base_url="https://eur.boox.com/api/1/") as client:
        ...     payload = {"mobi": "foo@bar.com"}
        ...     client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)

        Example 2, closing the connection manually. It is not recommended, but it's not my job to stop you from that.
        Notice that you can also use BooxUrl enum to not rely on strings for the base_url

        >>> from boox.models.enums import BooxUrl
        >>> client = Boox(base_url=BooxUrl.EUR)
        >>> payload = {"mobi": "foo@bar.com"}
        >>> client.users.send_verification_code(payload=payload)
        SendVerifyResponse(<0: SUCCESS>)
        >>> client.close()
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, client: HttpClient) -> None:
        self.client = client
        self.users = UsersApi(self)
        self._is_closed: bool = getattr(client, "is_closed", False)

        if self._is_closed:
            msg = f"Cannot initialize {self.__class__.__name__} with a client which has a closed connection"
            raise ValueError(msg)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        if not self.is_closed:
            warnings.warn("Boox client was not closed explicitly", ResourceWarning, stacklevel=2)
            self.close()

    @property
    def is_closed(self):
        """Property to check whether a client's connection is closed."""
        return self._is_closed

    def close(self):
        """An explicit way of closing the Boox client."""
        if not self.is_closed:
            self.client.close()
            self._is_closed = True
