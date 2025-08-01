import datetime
from typing import TYPE_CHECKING

from boox.models.config_users import SyncTokenResponse

if TYPE_CHECKING:
    from faker import Faker


def test_sync_token_response_parses_token_expiration_date_correctly(faker: "Faker"):
    token_expiry = faker.date_time(tzinfo=datetime.UTC).replace(microsecond=0)
    data = SyncTokenResponse.model_validate({
        "data": None,
        "message": faker.pystr(),
        "result_code": faker.random_digit(),
        "tokenExpiredAt": int(token_expiry.timestamp()),
    })
    assert not data.data
    assert data.token_expired_at == token_expiry
