from typing import Literal

import httpx
from pydantic import SecretStr, validate_call

from boox.api.users import UsersApi
from boox.models.enums import BooxDomain


class BooxClient:
    @validate_call()
    def __init__(self, *, url: BooxDomain, token: SecretStr | Literal[""] = "") -> None:
        self.client = httpx.Client(base_url=str(url))
        self.token: SecretStr | Literal[""] = token
        self.users = UsersApi(self)
