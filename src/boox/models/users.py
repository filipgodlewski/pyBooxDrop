import re
from contextlib import suppress
from typing import Annotated, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator, validate_email
from pydantic_core import PydanticCustomError

from boox.models.base import BaseResponse


def soft_validate_email(value: str) -> bool:
    with suppress(PydanticCustomError):
        return bool(validate_email(value))
    return False


class SendVerifyCodeRequest(BaseModel):
    """A request body for POST users/sendVerifyCode.

    Attributes:
        area_code (str | None): Optional. Required if `mobi` is an e-mail.
        mobi (str): Required. Either mobile number or e-mail.
        scene (str): ...
        verify (str): ...

    There are basically 2 important usages:
    - send code to mobile,
    - send code to email.

    Examples:
        >>> SendVerifyCodeRequest(area_code="+48", mobi="600123456")  # mobile
        >>> SendVerifyCodeRequest(mobi="foo@bar.com")  # email
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, str_strip_whitespace=True)

    mobi: Annotated[str, StringConstraints(min_length=6)]
    area_code: Annotated[str, StringConstraints(min_length=2, pattern=r"^\+\d+$")] | None = Field(default=None)
    scene: str = ""
    verify: str = ""

    @model_validator(mode="after")
    def check_area_code(self) -> Self:
        is_phone = bool(re.fullmatch(r"\d+", self.mobi))
        is_email = bool(soft_validate_email(self.mobi))

        if not is_phone and not is_email:
            raise ValueError("mobi field must either be an e-mail or a phone number")
        if is_phone and not self.area_code:
            raise ValueError("area_code must be provided if phone method is used")
        if is_email and self.area_code:
            raise ValueError("mobi and area_code are mutually exclusive")
        return self


class SendVerifyResponse(BaseResponse[str]):
    """Base response type with data being a str."""
