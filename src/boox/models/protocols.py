from collections.abc import MutableMapping
from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class HttpResponse(Protocol):
    """The minimal requirement for a response to work with the Boox class."""

    def raise_for_status(self) -> Self:
        """A method that either raises an error for non-2xx status code or passes self down."""
        ...

    def json(self, **kwargs: Any) -> Any:
        """A method that returns whatever json.loads would return, typically a dictionary."""
        ...


@runtime_checkable
class HttpClient(Protocol):
    """The minimal requirement for a client to work with the Boox class."""

    headers: Any | MutableMapping[str, str]

    def post(self, url: str, json: Any | None = None, *args: Any, **kwargs: Any) -> HttpResponse:
        """A method to request a `POST` type response."""
        ...

    def close(self) -> None:
        """A method to close the current or global connection."""
        ...
