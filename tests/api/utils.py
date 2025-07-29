import os
import re
import time
from collections.abc import Callable
from functools import wraps
from typing import Self
from urllib.parse import urljoin

from pydantic import SecretStr

from boox.client import BaseHttpClient, BaseHTTPError
from boox.models.enums import BooxUrl


def with_retry[**P, T](
    *, retries: int, delay: int, exceptions: tuple[type[BaseException], ...]
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result: T | None = None
            for attempt in range(retries):
                try:
                    result = func(*args, **kwargs)
                    break
                except exceptions:
                    if attempt == retries - 1:
                        raise
                    time.sleep(delay)
            if not result:
                raise ValueError("No value under result")
            return result

        return wrapper

    return decorator


class E2EConfig:
    _instance = None
    _initialized: bool = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.domain: BooxUrl = BooxUrl(os.environ["E2E_TARGET_DOMAIN"])
        self.email_address: str = os.environ["E2E_SMTP_EMAIL"]
        self.x_api_key: str = os.environ["E2E_SMTP_X_API_KEY"]
        self._verification_code: str | None = None
        self._token: SecretStr = SecretStr("")
        self._initialized = True

    @property
    def verification_code(self) -> str | None:
        return self._verification_code

    @verification_code.setter
    def verification_code(self, value: str):
        match = re.compile(r"\d{6}").fullmatch(value)
        if not match:
            raise ValueError("Verification code must contain 6 digits")
        self._verification_code = match.group()

    @property
    def token(self) -> SecretStr:
        return self._token

    @token.setter
    def token(self, value: SecretStr):
        self._token = value


class EmailProvider:
    def __init__(self, config: E2EConfig):
        self.config = config
        self.address = self.config.email_address
        self.client = BaseHttpClient()
        self.client.headers.update({
            "X-API-KEY": self.config.x_api_key,
            "Accept": "application/ld+json",
        })
        self.base_url = "https://api.smtp.dev"
        self.messages_url: str | None = None
        self.newest_message_url: str | None = None

    def _prepare_url(self, route: str) -> str:
        return urljoin(self.base_url, route)

    @with_retry(retries=5, delay=1, exceptions=(BaseHTTPError, IndexError, KeyError))
    def _get_mailbox_url(self) -> str:
        response = self.client.get(self._prepare_url("/accounts"))
        data = response.raise_for_status().json()

        member = data["member"][0]
        mailboxes: list[dict[str, str]] = member["mailboxes"]
        inbox = next(filter(lambda m: m["path"] == "INBOX", mailboxes))
        return inbox["@id"]

    @with_retry(retries=5, delay=1, exceptions=(BaseHTTPError, IndexError, KeyError))
    def _get_message_url(self) -> str:
        if not self.messages_url:
            raise ValueError("No INBOX messages url obtained yet")

        response = self.client.get(self._prepare_url(self.messages_url))
        data = response.raise_for_status().json()

        member: dict[str, str] = data["member"][0]
        return f"{self.messages_url}/{member["id"]}"

    @with_retry(retries=10, delay=1, exceptions=(BaseHTTPError, IndexError, KeyError))
    def _get_newest_message(self) -> str:
        if not self.newest_message_url:
            raise ValueError("No newest message url obtained yet")

        response = self.client.get(self._prepare_url(self.newest_message_url))
        data = response.raise_for_status().json()

        return data["text"]

    def get_newest_message(self) -> str:
        mailbox_url = self._get_mailbox_url()
        self.messages_url = f"{mailbox_url}/messages"
        self.newest_message_url = self._get_message_url()
        return self._get_newest_message()

    def cleanup_inbox(self):
        if not self.messages_url:
            raise ValueError("No INBOX messages url obtained yet")

        response = self.client.get(self._prepare_url(self.messages_url))
        data = response.raise_for_status().json()

        messages: list[dict[str, str]] = data["member"]
        message_ids = [m["id"] for m in messages]
        for message_id in message_ids:
            self.client.delete(self._prepare_url(f"{self.messages_url}/{message_id}")).raise_for_status()
