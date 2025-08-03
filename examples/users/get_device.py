"""Example on how to get device(s) data."""

from typing import TYPE_CHECKING, cast

from boox.core import Boox
from boox.models.enums import BooxUrl
from boox.models.users import DataDevice

if TYPE_CHECKING:
    from boox.models.users import DeviceInfoResponse

TOKEN = cast(str, ...)  # Just to make this example easier


with Boox(base_url=BooxUrl.PUSH, token=TOKEN) as boox:
    response: "DeviceInfoResponse" = boox.users.get_device_info()

# For `data` field, this response returns an array of objects.
# These objects are wrapped by `DataDevice` model
_data: tuple["DataDevice", ...] = response.data

for _item in _data:
    print(_item.height)
