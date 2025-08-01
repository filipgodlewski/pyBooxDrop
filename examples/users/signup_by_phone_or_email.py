"""Example on how to fetch the session token.

It will probably be your second step.

In this example it is assumed that the verification code was obtained.
"""

from typing import TYPE_CHECKING

from boox import Boox, BooxUrl
from boox.models.users import FetchTokenRequest

if TYPE_CHECKING:
    from pydantic import SecretStr

    from boox.models.users import FetchTokenResponse

with Boox(base_url=BooxUrl.PUSH) as boox:
    payload = FetchTokenRequest.model_validate({"mobi": "foo@bar.com", "code": "123456"})
    response: "FetchTokenResponse" = boox.users.fetch_session_token(payload=payload)

# By default, received token is hidden from __str__ and __repr__.
token: "SecretStr" = response.data.token
# But you can reveal it using `.get_secret_value()`
print(token.get_secret_value())
