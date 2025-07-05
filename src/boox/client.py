import json as jsonlib
import warnings
from typing import Any, Self
from urllib import request

from pydantic import ConfigDict, TypeAdapter, validate_call

from boox.api.users import UsersApi
from boox.models.enums import BooxUrl
from boox.models.protocols import HttpClient


class BaseResponse:
    def __init__(self, raw_response: bytes) -> None:
        self._raw_response = raw_response

    def raise_for_status(self) -> Self: ...

    def json(self, **kwargs: Any) -> Any:
        return jsonlib.loads(self._content, **kwargs)


class BaseClient:
    def post(self, url: str, json: Any | None = None) -> BaseResponse:
        data = jsonlib.dumps(json).encode("utf-8") if json else None
        req = request.Request(url=url, data=data, headers=self.headers, method="POST")
        with urllib.request.urlopen(req) as response:
            return BaseResponse(response.read())

    def close(self) -> None:
        pass


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
    def __init__(self, client: HttpClient | None = None) -> None:
        if is_closed := getattr(client, "is_closed", False):
            msg = f"Cannot initialize {self.__class__.__name__} with a client which has a closed connection"
            raise ValueError(msg)

        if base_url := getattr(client, "base_url", None):
            base_url = TypeAdapter(BooxUrl).validate_python(base_url)

        self._base_url: BooxUrl | None = base_url
        self._is_closed: bool = is_closed
        self.client = client or BaseClient()
        self.users = UsersApi(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        if not self.is_closed:
            warnings.warn("Boox client was not closed explicitly", ResourceWarning, stacklevel=2)
            self.close()

    @property
    def base_url(self) -> BooxUrl | None:
        return self._base_url

    @base_url.setter
    @validate_call()
    def base_url(self, value: BooxUrl):
        self._base_url = value

    @property
    def is_closed(self):
        """Property to check whether a client's connection is closed."""
        return self._is_closed

    def close(self):
        """An explicit way of closing the Boox client."""
        if not self.is_closed:
            self.client.close()
            self._is_closed = True
