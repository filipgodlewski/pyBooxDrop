from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, Protocol
from urllib.parse import urljoin

if TYPE_CHECKING:
    from boox.core import Boox


class HasBooxSession(Protocol):
    _session: "Boox"


class TokenMissingError(Exception):
    pass


class Api:
    """An abstract representation of a base API class.

    Although it doesn't inherit from ABC, this class is not meant to be used as a standalone class.
    """

    def __init__(self, session: "Boox"):
        if type(self) is Api:
            raise TypeError("Cannot instantiate abstract class Api directly")
        self._session = session

    def _prepare_url(self, endpoint: str) -> str:
        if self._session.base_url is None:
            msg = f"{type(self._session).__name__}.base_url must be filled"
            raise ValueError(msg)
        return urljoin(self._session.base_url.rstrip("/"), endpoint)

    def _post(self, *, endpoint: str, json: Any | None = None):
        return self._session.client.post(self._prepare_url(endpoint), json=json).raise_for_status()

    def _get(self, *, endpoint: str):
        return self._session.client.get(self._prepare_url(endpoint)).raise_for_status()


def requires_token[T: Api, **P, R](func: Callable[Concatenate[T, P], R]) -> Callable[Concatenate[T, P], R]:
    @wraps(func)
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self._session.token:  # pyright: ignore[reportPrivateUsage]
            raise TokenMissingError("Bearer token is required to call this method")
        return func(self, *args, **kwargs)

    return wrapper
