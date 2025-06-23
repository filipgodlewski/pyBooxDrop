from abc import ABC
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from boox.models.enums import BooxDomain


class BooxApiUrl(BaseModel):
    """A helper model for generating proper API url.

    Attributes:
        domain (BooxDomain): The server the account is registered on.
        version (int): The API version. Currently only v1 is officially published.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, use_enum_values=True)

    domain: BooxDomain
    version: int = Field(default=1, strict=True, ge=1, description="API version. Currently only `1` is supported.")

    def __str__(self) -> str:
        return f"https://{self.domain}/api/{self.version}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)!r})"


class BaseResponse[T](BaseModel, ABC):
    """General server response.

    Attributes:
        data (T | None): Arbitrary response data.
        message (str): The response message.
        result_code (int): Internal result code.
    """

    data: T | None
    message: str
    result_code: int
