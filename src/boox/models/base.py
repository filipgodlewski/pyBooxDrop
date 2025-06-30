from abc import ABC

from pydantic import BaseModel


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
