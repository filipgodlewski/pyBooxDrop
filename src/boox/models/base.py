from abc import ABC
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, RootModel

from boox.models.enums import BooxDomain


class BooxApiUrl(RootModel[BooxDomain]):
    """A helper model for generating proper API url.

    Attributes:
        domain (BooxDomain): The server the account is registered on.
        version (int): The API version. Currently only v1 is officially published.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, use_enum_values=True)
    root: BooxDomain

    def __str__(self) -> str:
        return f"https://{self.root}/api/1"

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

    def __str__(self) -> str:
        return f"<{self.result_code}: {self.message}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self!s})"
