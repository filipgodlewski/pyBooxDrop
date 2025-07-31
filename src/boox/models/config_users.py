from boox.models.base import BaseSyncResponse


class SyncTokenResponse(BaseSyncResponse[None]):
    """A response, wtih information about token expiry date."""
