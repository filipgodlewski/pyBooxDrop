from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from boox.models.base import BaseResponse, BaseSyncResponse

if TYPE_CHECKING:
    from faker import Faker


def test_base_response_str_format(faker: "Faker"):
    message = faker.pystr()
    result_code = faker.random_digit()
    response = BaseResponse(data=None, message=message, result_code=result_code)
    assert str(response) == f"<{result_code}: {message}>"


def test_subclass_response_repr_format(faker: "Faker"):
    message = faker.pystr()
    result_code = faker.random_digit()

    class DummyResponse(BaseResponse[None]): ...

    response = DummyResponse(data=None, message=message, result_code=result_code)
    assert repr(response) == f"DummyResponse(<{result_code}: {message}>)"


def test_base_sync_subclass_raises_error_if_no_token_expiry_date_provided(faker: "Faker"):
    class DummySyncResponse(BaseSyncResponse[None]): ...

    with pytest.raises(ValidationError, match="Field required"):
        DummySyncResponse.model_validate({"data": None, "message": faker.pystr(), "result_code": faker.random_digit()})
