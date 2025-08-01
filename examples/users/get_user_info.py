"""Example on how to get user data.

Quite a useful method if you'd like to see whether the changes to the account were applied.
"""

from typing import cast

from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import UserInfoResponse

TOKEN = cast(str, ...)  # Just to make this example easier


with Boox(base_url=BooxUrl.PUSH, token=TOKEN) as boox:
    response: UserInfoResponse = boox.users.get_user_info()


# This response contains a lot of data about your account
# Most notable are listed below.
# login_type - how you logged in
_login_type: str = response.data.login_type

# nickname - your custom name for the account
_nickname: str = response.data.nickname

# storage_usd and storage_limit
_storage_used: int = response.data.storage_used
_storage_limit: int = response.data.storage_limit
