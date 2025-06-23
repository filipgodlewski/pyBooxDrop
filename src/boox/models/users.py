from contextlib import suppress
from typing import Annotated, ClassVar, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
    validate_email,
)

from boox.models.base import BaseResponse


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
    has_email: ClassVar[bool] = False

    area_code: Annotated[str, StringConstraints(min_length=2, pattern=r"^\+\d+")] | None = Field(default=None)
    mobi: Annotated[str, StringConstraints(pattern=r"\d+")] | EmailStr
    scene: str = ""
    verify: str = ""

    @field_validator("mobi", mode="before")
    @classmethod
    def mark_email(cls, value: str) -> str:
        with suppress(ValidationError):
            _ = validate_email(value)
            cls.has_email = True
        return value

    @model_validator(mode="after")
    def check_area_code(self) -> Self:
        if self.__class__.has_email and self.area_code:
            raise ValueError("E-mail and area code are mutually exclusive. Maybe area_code should be None?")
        return self


class SendVerifyResponse(BaseResponse[str]):
    """Base response type with data being a str."""
