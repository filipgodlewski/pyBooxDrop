import datetime
import re

import pytest
from pydantic import ValidationError

from boox.models.users import (
    DataSession,
    DataToken,
    FetchTokenRequest,
    SendVerifyCodeRequest,
    SyncTokenResponse,
    soft_validate_email,
)

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


def test_token_str_is_masked():
    data = DataToken.model_validate({"token": "xyz123"})
    assert re.compile(r"\*+").fullmatch(str(data.token))


def test_token_is_public_in_model_dump():
    value = "xyz123"
    data = DataToken.model_validate({"token": value})
    dumped = data.model_dump()
    assert dumped.get("token") == value


def test_token_is_public_in_json_dump():
    value = "xyz123"
    data = DataToken.model_validate({"token": value})
    dumped = data.model_dump_json()
    assert re.compile(r'{"token":"xyz123"}').fullmatch(dumped)


def test_sync_token_response_parses_nested_data_correctly():
    data = SyncTokenResponse.model_validate({
        "data": {
            "channels": (),
            "cookie_name": "foo",
            "expires": datetime.datetime.now(tz=datetime.UTC),
            "session_id": "bar",
        },
        "message": "SUCCESS",
        "result_code": 0,
        "tokenExpiredAt": 1,
    })
    assert isinstance(data.data, DataSession)
    assert data.token_expired_at
