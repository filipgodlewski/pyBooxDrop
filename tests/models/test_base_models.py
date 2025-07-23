from boox.models.base import BaseResponse


def test_base_response_str_format():
    response = BaseResponse[None](data=None, message="foo", result_code=123)
    assert str(response) == "<123: foo>"


def test_subclass_response_repr_format():
    class DummyResponse(BaseResponse[None]): ...

    response = DummyResponse(data=None, message="foo", result_code=123)
    assert repr(response) == "DummyResponse(<123: foo>)"
