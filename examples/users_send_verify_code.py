"""Example on how to send the verification code.

This basically, in many situations, is your first step when using the library.

The example is divided into 2 parts:
    - robust, using all available types,
    - simplified, which still should pass (in case you have very loose static analysis rules)

Bear in mind that since this library is heavily validated on many steps,
You probably are ok with the simplified version.
Mix and match however you like.
"""

from boox.client import BooxClient

# Example 1: robust
from boox.models.base import BooxApiUrl
from boox.models.enums import BooxDomain

client = BooxClient(url=BooxApiUrl(BooxDomain.EUR))

# Example 2: simplified
# pyright: reportArgumentType=false

client = BooxClient(url="eur.boox.com")
