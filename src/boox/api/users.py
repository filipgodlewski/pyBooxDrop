from pydantic import validate_call

from boox.api.core import Api, requires_token
from boox.models.users import (
    FetchTokenRequest,
    FetchTokenResponse,
    SendVerifyCodeRequest,
    SendVerifyResponse,
    SyncTokenResponse,
)


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

        This method is used **before** authentication. Luckily, it is not necessary to use it every single time,
        because the tokens received after verification expire every 20 days.

        Args:
            payload (SendVerifyCodeRequest): The validated payload to be sent in order to receive the verification code.

        Returns:
            SendVerifyResponse: The validated, generic response that is always received from the server.
        """
        response = self._post(endpoint="/api/1/users/sendVerifyCode", json=payload.model_dump(exclude_unset=True))
        return SendVerifyResponse.model_validate(response.json())

    @validate_call()
    def fetch_session_token(self, *, payload: FetchTokenRequest) -> FetchTokenResponse:
        """A call to sign in using the obtained verification code.

        Once a verification code is received, it can be used for this request in a payload, along the verification method used in
        send_verification_code method above.

        This method is the vertification. It allows you to receive the session token used in many other requests of all types.

        Args:
            payload (FetchTokenRequest): The validated payload to be sent in order to fetch the session token.

        Returns:
            FetchTokenResponse: The validated response containing a session token.
        """
        response = self._post(endpoint="/api/1/users/signupByPhoneOrEmail", json=payload.model_dump(exclude_unset=True))
        return FetchTokenResponse.model_validate(response.json())

    @requires_token
    def synchronize_token(self) -> SyncTokenResponse:
        """A call to check token authenticity and validity.

        A typical scenario for this route is to use it before any action to prevent a server error.

        This call **requires** the token to be passed as an Authorization header, e.g.:
            >>> {"Authorization": "Bearer xyz123abc"}
        That is also the reason why this call pre-validates the client header.

        Returns:
            SyncTokenResponse: The validated response containing information about token expiry date, and session metadata.
        """
        response = self._get(endpoint="/api/1/users/syncToken")
        return SyncTokenResponse.model_validate(response.json())
