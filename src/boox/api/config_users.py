from boox.api.core import Api, requires_token
from boox.models.config_users import SyncTokenResponse


class ConfigUsersApi(Api):
    """API wrappers for `configUsers` endpoint family.

    Note that since Boox class already has ConfigUsersApi in its context,
    it is not recommended to use ConfigUsersApi as a standalone object.
    """

    @requires_token
    def synchronize_token(self) -> SyncTokenResponse:
        """A call to check token authenticity and validity.

        A typical scenario for this route is to use it before any action to prevent a server error.

        This call **requires** the token to be passed as an Authorization header, e.g.:
            >>> {"Authorization": "Bearer xyz123abc"}
        That is also the reason why this call pre-validates the client header.

        Returns:
            SyncTokenResponse: The validated response containing information about token expiry date.
        """
        response = self._get(endpoint="/api/1/configUsers/one")
        return SyncTokenResponse.model_validate(response.json())
