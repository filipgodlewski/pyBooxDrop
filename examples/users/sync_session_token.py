"""Example on how to synchronize session token.

While this method is not required at all, especially if you write short scripts,
it makes sense to use it occasionally to make sure that you don't use an expired token.
But you might want to use it only if you rely on the session_id.
"""

import datetime
from typing import cast

from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import SyncSessionTokenResponse

TOKEN = cast(str, ...)  # Just to make this example easier


with Boox(base_url=BooxUrl.EUR, token=TOKEN) as boox:
    response: SyncSessionTokenResponse = boox.users.synchronize_session_token()

_: datetime.datetime = response.data.expires
