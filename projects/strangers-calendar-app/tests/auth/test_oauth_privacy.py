|
import unittest
from backend.auth.oauth import get_ephemeral_access_token

class TestOAuthPrivacy(unittest.TestCase):
def test_ephemeral_access_token_expiration(self):
# Simulate getting an ephemeral access token
token = get_ephemeral_access_token()

# Verify that the token is an instance of EphemeralAccessToken
self.assertIsInstance(token, EphemeralAccessToken)

# Verify that the token has a limited expiration time (e.g., 1 hour)
current_time = datetime.datetime.now()
expiration_time = current_time + datetime.timedelta(hours=1)
self.assertLessEqual(token.expiration_time, expiration_time)
