import json
import re
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from boox.models.users import (
    DataToken,
    FetchTokenRequest,
    SendVerifyCodeRequest,
    soft_validate_email,
)

if TYPE_CHECKING:
    from faker import Faker


def test_soft_validate_email_returns_true_for_valid_email(faker: "Faker"):
    is_email = soft_validate_email(faker.email())
    assert is_email


def test_soft_validate_email_returns_false_for_invalid_email(faker: "Faker"):
    is_email = soft_validate_email(faker.email(domain=faker.random_lowercase_letter()))
    assert not is_email


def test_validation_fails_when_mobi_is_empty_string():
    with pytest.raises(ValidationError, match="String should have at least 6 characters"):
        SendVerifyCodeRequest.model_validate({"mobi": ""})


def test_validation_requires_area_code_for_phone_number(faker: "Faker"):
    with pytest.raises(ValidationError, match="area_code must be provided if phone method is used"):
        SendVerifyCodeRequest.model_validate({"mobi": str(faker.msisdn())})


def test_validation_fails_when_area_code_does_not_match_pattern(faker: "Faker"):
    with pytest.raises(ValidationError, match="String should match pattern"):
        SendVerifyCodeRequest.model_validate({
            "mobi": str(faker.msisdn()),
            "area_code": faker.country_calling_code().replace("+", "00"),
        })


def test_validation_fails_when_mobi_is_neither_email_nor_phone(faker: "Faker"):
    with pytest.raises(ValidationError, match="mobi field must either be an e-mail or a phone number"):
        SendVerifyCodeRequest.model_validate({"mobi": faker.email(domain=faker.random_lowercase_letter())})


def test_validation_fails_when_email_and_area_code_are_both_provided(faker: "Faker"):
    with pytest.raises(ValidationError, match="mobi and area_code are mutually exclusive"):
        SendVerifyCodeRequest.model_validate({"mobi": faker.email(), "area_code": faker.country_calling_code()})


def test_validation_allows_email_without_area_code(faker: "Faker"):
    assert SendVerifyCodeRequest.model_validate({"mobi": faker.email()})


def test_validation_fails_when_verification_code_does_not_match_pattern(faker: "Faker"):
    with pytest.raises(ValidationError, match="String should match pattern"):
        FetchTokenRequest.model_validate({"mobi": faker.email(), "code": str(faker.random_number(digits=7))})


def test_validation_succeeds_when_verification_code_matches_pattern(faker: "Faker"):
    assert FetchTokenRequest.model_validate({"mobi": faker.email(), "code": str(faker.random_number(digits=6))})


def test_token_str_is_masked(faker: "Faker"):
    data = DataToken.model_validate({"token": faker.uuid4()})
    assert re.compile(r"\*+").fullmatch(str(data.token))


def test_token_is_public_in_model_dump(faker: "Faker"):
    value = faker.uuid4()
    data = DataToken.model_validate({"token": value})
    dumped = data.model_dump()
    assert dumped.get("token") == value


def test_token_is_public_in_json_dump(faker: "Faker"):
    data = {"token": faker.uuid4()}
    model = DataToken.model_validate(data)
    dumped = model.model_dump_json()
    assert json.dumps(data, separators=(", ", ":")) == dumped
