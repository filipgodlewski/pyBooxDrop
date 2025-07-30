import datetime
import re
from contextlib import suppress
from typing import Annotated, Any, ClassVar, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    SecretStr,
    StringConstraints,
    model_validator,
    validate_email,
)
from pydantic_core import PydanticCustomError

from boox.models.base import BaseResponse, BaseSyncResponse


def soft_validate_email(value: str) -> bool:
    with suppress(PydanticCustomError):
        return bool(validate_email(value))
    return False


class BaseVerificationModel(BaseModel):
    """The base request body for verification and authentication requests.

    Attributes:
        area_code (str | None): Optional. Required if `mobi` is an e-mail.
        mobi (str): Required. Either mobile number or e-mail.

    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, str_strip_whitespace=True)

    mobi: Annotated[str, StringConstraints(min_length=6)]
    area_code: Annotated[str, StringConstraints(min_length=2, pattern=r"^\+\d+$")] | None = Field(default=None)

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


class SendVerifyCodeRequest(BaseVerificationModel):
    """A request body for POST users/sendVerifyCode.

    Please refer to BaseVerificationModel for more attributes.

    Attributes:
        scene (str): Unknown.
        verify (str): Unknown.

    There are basically 2 important usages:
    - send code to mobile,
    - send code to email.

    Examples:
        >>> SendVerifyCodeRequest(area_code="+48", mobi="600123456")  # mobile
        >>> SendVerifyCodeRequest(mobi="foo@bar.com")  # email
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, str_strip_whitespace=True)

    scene: str = ""
    verify: str = ""


class SendVerifyResponse(BaseResponse[str]):
    """Base response type with data being a str."""


class FetchTokenRequest(BaseVerificationModel):
    """A request body for POST users/signupByPhoneOrEmail.

    Attributes:
        code (str): The verification code received via either mobile or e-mail.

    Note:
        Verification code is 6 digits long, but is passed as a string.
    """

    code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")]


class DataToken(BaseModel):
    token: Annotated[SecretStr, PlainSerializer(lambda v: v.get_secret_value(), return_type=str, when_used="always")]


class FetchTokenResponse(BaseResponse[DataToken]):
    """A response, with token under data key."""


class DataSession(BaseModel):
    channels: tuple[Any, ...]
    cookie_name: str
    expires: datetime.datetime
    session_id: SecretStr


class SyncSessionTokenResponse(BaseSyncResponse[DataSession]):
    """A response, with information about expiry dates, with an emphasis on the session."""
