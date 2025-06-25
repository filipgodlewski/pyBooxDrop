from typing import TYPE_CHECKING

from pydantic import validate_call

from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse

if TYPE_CHECKING:
    from boox.client import BooxClient


class UsersApi:
    """API wrappers for users/ endpoint family.

    NOTE: Since BooxClient class already has UsersApi in its context,
    it is not recommended to use UsersApi as a standalone object.
    """

    def __init__(self, session: "BooxClient") -> None:
        self._session = session

    @validate_call()
    def send_verification_code(self, *, payload: SendVerifyCodeRequest) -> SendVerifyResponse:
        """Initial call to get the verification code.

        Depending on the payload, it will either send the verification code on provided e-mail or phone number.
        For phone numbers, works internationally, depending on the provided area code.

        The verification code is valid for 5 minutes.
        The official BOOXDrop service has a 1 minute countdown before you can resend the code (for a particular method).

        Since this method is used **before** authentication, it has to be a staticmethod.
        Luckily, it is not necessary to use it every single time, because the tokens received after verification
        are expiring every 20 days.

        Args:
            base_url (BooxApiUrl): The url to the server the account is registered on.
            payload (SendVerifyCodeRequest): The validated payload to be sent in order to receive the verification code.

        Returns:
            SendVerifyResponse: The validated, generic response that is always received from the server.
        """
        with self._session.client as client:
            response = client.post("users/sendVerifyCode", json=payload.model_dump_json())

        data = response.raise_for_status().text
        return SendVerifyResponse.model_validate_json(data)
