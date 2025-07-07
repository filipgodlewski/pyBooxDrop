from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

if TYPE_CHECKING:
    from boox.core import Boox


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
            msg = f"{self._session.__class__.__name__}.base_url must be filled"
            raise ValueError(msg)
        return urljoin(self._session.base_url, endpoint.lstrip("/"))

    def _post(self, *, endpoint: str, json: Any | None = None):
        return self._session.client.post(self._prepare_url(endpoint), json=json).raise_for_status()
