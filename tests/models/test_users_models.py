import pytest
from pydantic import ValidationError

from boox.models.users import FetchTokenRequest, SendVerifyCodeRequest, soft_validate_email

EMAIL = "foo@bar.com"
INVALID_EMAIL = "foobar@baz"


def test_soft_validate_email_returns_true_for_valid_email():
    is_email = soft_validate_email(EMAIL)
    assert is_email


def test_soft_validate_email_returns_false_for_invalid_email():
    is_email = soft_validate_email(INVALID_EMAIL)
    assert not is_email


def test_validation_fails_when_mobi_is_empty_string():
    with pytest.raises(ValidationError, match="String should have at least 6 characters"):
        SendVerifyCodeRequest.model_validate({"mobi": ""})


def test_validation_requires_area_code_for_phone_number():
    with pytest.raises(ValidationError, match="area_code must be provided if phone method is used"):
        SendVerifyCodeRequest.model_validate({"mobi": "123456789"})


def test_validation_fails_when_area_code_does_not_match_pattern():
    with pytest.raises(ValidationError, match="String should match pattern"):
        SendVerifyCodeRequest.model_validate({"mobi": "123456789", "area_code": "0048"})


def test_validation_fails_when_mobi_is_neither_email_nor_phone():
    with pytest.raises(ValidationError, match="mobi field must either be an e-mail or a phone number"):
        SendVerifyCodeRequest.model_validate({"mobi": INVALID_EMAIL})


def test_validation_fails_when_email_and_area_code_are_both_provided():
    with pytest.raises(ValidationError, match="mobi and area_code are mutually exclusive"):
        SendVerifyCodeRequest.model_validate({"mobi": EMAIL, "area_code": "+48"})


def test_validation_allows_email_without_area_code():
    assert SendVerifyCodeRequest.model_validate({"mobi": EMAIL})


def test_validation_fails_when_verification_code_does_not_match_pattern():
    with pytest.raises(ValidationError, match="String should match pattern"):
        FetchTokenRequest.model_validate({"mobi": EMAIL, "code": "1234567"})


def test_validation_succeeds_when_verification_code_matches_pattern():
    assert FetchTokenRequest.model_validate({"mobi": EMAIL, "code": "123456"})
