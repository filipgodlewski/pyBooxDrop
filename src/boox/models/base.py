import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class BaseResponse[T](BaseModel):
    """General server response.

    Attributes:
        data (T | None): Arbitrary response data.
        message (str): The response message.
        result_code (int): Internal result code.
    """

    data: T
    message: str
    result_code: int

    def __str__(self) -> str:
        return f"<{self.result_code}: {self.message}>"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self!s})"


class BaseSyncResponse[T](BaseResponse[T]):
    """A base response for responses that rely on token."""

    model_config: ClassVar[ConfigDict] = ConfigDict(serialize_by_alias=True)

    token_expired_at: datetime.datetime = Field(alias="tokenExpiredAt")
