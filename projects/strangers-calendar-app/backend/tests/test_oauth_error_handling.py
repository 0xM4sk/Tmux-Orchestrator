|
import unittest
from backend.auth.oauth import google_auth, apple_auth

class TestOAuthErrorHandling(unittest.TestCase):
def test_google_auth_failure(self):
# Mock the external API response for failure
with self.assertRaises(Exception):
google_auth()

def test_apple_auth_failure(self):
# Mock the external API response for failure
with self.assertRaises(Exception):
apple_auth()

if __name__ == '__main__':
unittest.main()