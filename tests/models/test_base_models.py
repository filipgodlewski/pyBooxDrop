import pytest
from pydantic import ValidationError

from boox.models.base import BaseResponse, BaseSyncResponse


def test_base_response_str_format():
    response = BaseResponse(data=None, message="foo", result_code=123)
    assert str(response) == "<123: foo>"


def test_subclass_response_repr_format():
    class DummyResponse(BaseResponse[None]): ...

    response = DummyResponse(data=None, message="foo", result_code=123)
    assert repr(response) == "DummyResponse(<123: foo>)"


def test_base_sync_subclass_raises_error_if_no_token_expiry_date_provided():
    class DummySyncResponse(BaseSyncResponse[None]): ...

    with pytest.raises(ValidationError, match=r"Field required"):
        DummySyncResponse.model_validate({"data": None, "message": "foo", "result_code": 123})
