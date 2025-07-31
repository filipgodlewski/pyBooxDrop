import datetime
import re
from contextlib import suppress
from typing import Annotated, Any, ClassVar, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
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


class DataUser(BaseModel):
    # NOTE: If having `Any`, it means that it lacks information on type based on my internal testing.
    # If you have some additional data, please contribute.
    model_config: ClassVar[ConfigDict] = ConfigDict(serialize_by_alias=True)

    access_token: Any | None = Field(alias="accessToken")
    area_code: Annotated[str, StringConstraints(min_length=2, pattern=r"^\+\d+$")]
    avatar: Any | None
    avatar_url: Any | None = Field(alias="avatarUrl")
    children: tuple[Any, ...]
    consecutive_usage_days: int = Field(alias="consecutiveUsageDays")
    device_limit: int
    email: EmailStr
    gift_count: int = Field(alias="giftCount")
    google_id: Any | None
    huawei_id: Any | None
    id: int
    login_type: str
    nickname: str
    oauth_id: Any | None
    otp_auth_url: Any | None
    otp_enabled: bool
    otp_verified: bool
    parent: Any | None
    phone: str
    role_value: int = Field(alias="roleValue")
    sex: Any | None
    storage_limit: int
    storage_used: int
    total_doc_count: int = Field(alias="totalDocCount")
    total_usage_days: int = Field(alias="totalUsageDays")
    uid: str
    vip_cloud: int
    vip_cloud_end: Any | None
    vip_cloud_start: Any | None
    wechat_id: Any | None


class UserInfoResponse(BaseSyncResponse[DataUser]):
    """A response with basic user information."""
