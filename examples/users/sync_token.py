"""Example on how to synchronize token.

While this method is not required at all, especially if you write short scripts,
it makes sense to use it occasionally to make sure that you don't use an expired token.
"""

import datetime
from typing import cast

from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import SyncTokenResponse

TOKEN = cast(str, ...)  # Just to make this example easier


with Boox(base_url=BooxUrl.EUR, token=TOKEN) as boox:
    response: SyncTokenResponse = boox.users.synchronize_token()

# Although the original response has tokenExpiredAt key, it is aliased for more pythonic use

# In the original response it is an integer, which in fact is a UNIX epoch timestamp.
# For example 1768815112 is an equivalent of GMT: Monday, 19 January 2026 09:31:52.
# For convenience, it is being cast to the datetime.datetime object during data validation.
_: datetime.datetime = response.token_expired_at
