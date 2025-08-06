|
import unittest
from backend.auth.oauth import validate_credentials

class TestAuthOAuthEdgeCases(unittest.TestCase):
def test_invalid_credentials(self):
# Test case for invalid credentials
self.assertFalse(validate_credentials("invalid_user", "invalid_password"))

def test_unauthorized_request(self):
# Test case for unauthorized request
self.assertEqual(validate_credentials(None, None), False)

if __name__ == '__main__':
unittest.main()