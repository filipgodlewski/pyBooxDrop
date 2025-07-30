import datetime

from boox.models.config_users import SyncTokenResponse


def test_sync_token_response_parses_token_expiration_date_correctly():
    token_expiry = datetime.datetime.now(tz=datetime.UTC).replace(microsecond=0) + datetime.timedelta(days=180)
    data = SyncTokenResponse.model_validate({
        "data": None,
        "message": "SUCCESS",
        "result_code": 0,
        "tokenExpiredAt": int(token_expiry.timestamp()),
    })
    assert not data.data
    assert data.token_expired_at == token_expiry
