import pytest
from pydantic import ValidationError

from boox.models.users import SendVerifyCodeRequest, soft_validate_email


def test_soft_validate_email_returns_true_for_valid_email():
    is_email = soft_validate_email("foo@bar.com")
    assert is_email


def test_soft_validate_email_returns_false_for_invalid_email():
    is_email = soft_validate_email("foobar.baz")
    assert not is_email


def fail_mobi_validation(data: dict[str, str]) -> str:
    with pytest.raises(ValidationError) as err:
        SendVerifyCodeRequest.model_validate(data)
    error = next(iter(err.value.errors()))
    return error["msg"]


def test_validation_fails_when_mobi_is_empty_string():
    message = fail_mobi_validation({"mobi": ""})
    assert message == "String should have at least 1 character"


def test_validation_requires_area_code_for_phone_number():
    message = fail_mobi_validation({"mobi": "123456789"})
    assert message == "Value error, Area code must be provided if phone method is used."


def test_validation_fails_when_mobi_is_neither_email_nor_phone():
    message = fail_mobi_validation({"mobi": "foobar.baz"})
    assert message == "Value error, The `mobi` field must either be an e-mail or a phone number."


def test_validation_fails_when_email_and_area_code_are_both_provided():
    message = fail_mobi_validation({"mobi": "foo@bar.com", "area_code": "+48"})
    assert message == "Value error, E-mail and area code are mutually exclusive."


def test_validation_allows_email_without_area_code():
    data = {"mobi": "foo@bar.com"}
    assert SendVerifyCodeRequest.model_validate(data)
