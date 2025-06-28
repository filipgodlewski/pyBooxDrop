import os
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from httpx import Client, HTTPStatusError

P = ParamSpec("P")
T = TypeVar("T")


def with_retry(
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


class EmailProvider:
    def __init__(self):
        self.address = os.environ["E2E_SMTP_EMAIL"]
        x_api_key = os.environ["E2E_SMTP_X_API_KEY"]
        headers = {"X-API-KEY": x_api_key, "accept": "application/ld+json"}
        base_url = "https://api.smtp.dev"
        self.client = Client(base_url=base_url, headers=headers)
        self.message_url: str | None = None

    @with_retry(retries=3, delay=1, exceptions=(HTTPStatusError, IndexError, KeyError))
    def _get_mailbox_url(self) -> str:
        with self.client as client:
            response = client.get("accounts")
        data = response.raise_for_status().json()

        member = data["member"][0]
        mailboxes: list[dict[str, str]] = member["mailboxes"]
        inbox = next(filter(lambda m: m["path"] == "INBOX", mailboxes))
        return inbox["@id"]

    @with_retry(retries=3, delay=1, exceptions=(HTTPStatusError, IndexError, KeyError))
    def _get_message_url(self, endpoint_url: str) -> str:
        with self.client as client:
            response = client.get(endpoint_url)
        data = response.raise_for_status().json()

        member: dict[str, str] = data["member"][0]
        return f"{endpoint_url}/{member["id"]}"

    @with_retry(retries=3, delay=3, exceptions=(HTTPStatusError, IndexError, KeyError))
    def _get_message(self) -> str:
        if not self.message_url:
            raise ValueError("No message url obtained yet")

        with self.client as client:
            response = client.get(self.message_url)

        data = response.raise_for_status().json()
        return data["text"]

    def get_verification_code(self) -> str:
        mailbox_url = self._get_mailbox_url()
        self.message_url = self._get_message_url(f"{mailbox_url}/messages")
        return self._get_message()

    def try_delete_message(self):
        if not self.message_url:
            raise ValueError("No message url obtained yet")

        with self.client as client:
            client.delete(self.message_url)
