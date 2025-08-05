|
import unittest
from app.auth.oauth import get_google_auth_url, get_apple_auth_url

class TestOAuthEdgeCases(unittest.TestCase):
def test_empty_token(self):
with self.assertRaises(ValueError):
get_google_auth_url(token="")

def test_invalid_token(self):
with self.assertRaises(ValueError):
get_google_auth_url(token="invalid_token")

def test_expired_token(self):
with self.assertRaises(ExpiredTokenError):
get_google_auth_url(token="expired_token")

def test_multiple_attempts(self):
# Simulate multiple authentication attempts
for _ in range(10):
try:
get_google_auth_url(token="valid_token")
except Exception as e:
self.fail(f"Authentication attempt failed: {e}")

if __name__ == '__main__':
unittest.main()