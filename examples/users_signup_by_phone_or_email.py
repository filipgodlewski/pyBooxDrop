"""Example on how to fetch the session token.

It will probably be your second step.

In this example it is assumed that the verification code was obtained.
"""

from boox import Boox, BooxUrl
from boox.models.users import FetchTokenRequest, FetchTokenResponse

with Boox(base_url=BooxUrl.PUSH) as boox:
    payload = FetchTokenRequest(mobi="foo@bar.com", code="123456")
    response: FetchTokenResponse = boox.users.fetch_session_token(payload=payload)

_: str = response.data.token
