"""Example on how to send the verification code.

This basically, in many situations, is your first step when using the library.

The example is divided into 2 parts:
    - robust, using all available types,
    - simplified, which still should pass (in case you have very loose static analysis rules)

Bear in mind that since this library is heavily validated on many steps,
You probably are ok with the simplified version.
Mix and match however you like.
"""

from boox.core import Boox

# Example 1: robust
from boox.models.enums import BooxUrl
from boox.models.users import SendVerifyCodeRequest

with Boox(base_url=BooxUrl.EUR) as client:
    payload = SendVerifyCodeRequest(mobi="foo@bar.com")
    _ = client.users.send_verification_code(payload=payload)

# Example 2: simplified
# pyright: reportArgumentType=false

# Here, in this example I don't use a context manager, and I close the connection manually.
# It does not mean that you have to use it like that.
# In fact, I highly recommend using Boox as a context manager.
# This is similar to using builtins.open().

client = Boox(base_url="eur.boox.com")
payload = {"mobi": "foo@bar.com"}
_ = client.users.send_verification_code(payload=payload)
client.close()
