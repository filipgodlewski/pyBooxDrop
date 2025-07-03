from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class HttpResponse(Protocol):
    """The minimal requirement for a response to work with the Boox class."""

    def raise_for_status(self) -> Self: ...
    def json(self) -> Any: ...


@runtime_checkable
class HttpClient(Protocol):
    """The minimal requirement for a client to work with the Boox class."""

    def post(self, url: str, json: Any | None = None, *args: Any, **kwargs: Any) -> HttpResponse: ...
    def close(self) -> None: ...
