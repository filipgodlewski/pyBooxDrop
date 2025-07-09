import json as jsonlib
from http import HTTPStatus
from typing import Any, Self
from urllib.request import Request, urlopen

from pydantic import validate_call


class BaseHTTPError(Exception):
    """Base HTTP exception."""

    def __init__(self, url: str, code: HTTPStatus, headers: dict[str, str], content: bytes) -> None:
        self.url = url
        self.code = code
        self.headers = headers
        self._content = content

    @property
    def content(self) -> str:
        return self._content.decode()

    def __str__(self) -> str:
        return f"HTTP Error {self.code.value}: {self.code.phrase}"

    def __repr__(self) -> str:
        return f"<HTTP Error {self.code.value}: {self.code.phrase!r}>"


class BaseHttpResponse:
    def __init__(self, *, code: HTTPStatus, url: str, headers: dict[str, str], content: bytes) -> None:
        self._code = code
        self._url = url
        self._headers = headers
        self._content = content

    def __repr__(self) -> str:
        return f"<Response [{self._code.value}]>"

    def raise_for_status(self) -> Self:
        if self._code.is_success:
            return self
        raise BaseHTTPError(url=self._url, code=self._code, headers=self._headers, content=self._content)

    def json(self, **kwargs: Any) -> Any:
        return jsonlib.loads(self._content, **kwargs)


class BaseHttpClient:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}

    def _build_request(self, method: str, url: str, json: Any | None) -> Request:
        data = jsonlib.dumps(json).encode() if json else None
        return Request(url=url, data=data, headers=self.headers, method=method)

    @staticmethod
    def _send(request: Request) -> BaseHttpResponse:
        with urlopen(request) as response:
            return BaseHttpResponse(
                code=HTTPStatus(response.status),
                url=response.geturl(),
                headers=response.headers,
                content=response.read(),
            )

    @validate_call()
    def post(self, url: str, json: Any | None = None) -> BaseHttpResponse:
        request = self._build_request("POST", url, json)
        return self._send(request)

    @validate_call()
    def get(self, url: str) -> BaseHttpResponse:
        request = self._build_request("GET", url, None)
        return self._send(request)

    @validate_call()
    def delete(self, url: str) -> BaseHttpResponse:
        request = self._build_request("DELETE", url, None)
        return self._send(request)

    def close(self) -> None:
        pass
