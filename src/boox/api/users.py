from pydantic import validate_call

from boox.api.core import Api
from boox.models.users import SendVerifyCodeRequest, SendVerifyResponse


class UsersApi(Api):
    """API wrappers for `users` endpoint family.

    Note that since Boox class already has UsersApi in its context,
    it is not recommended to use UsersApi as a standalone object.
    """

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
            payload (SendVerifyCodeRequest): The validated payload to be sent in order to receive the verification code.

        Returns:
            SendVerifyResponse: The validated, generic response that is always received from the server.
        """
        response = self._post(endpoint="/users/sendVerifyCode", json=payload.model_dump(exclude_unset=True))
        return SendVerifyResponse.model_validate(response.json())
