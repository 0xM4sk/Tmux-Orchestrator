|
from backend.auth.oauth import get_google_auth_url
import unittest

class TestOAuth(unittest.TestCase):
def test_get_google_auth_url(self):
# Arrange
expected_url = "https://accounts.google.com/o/oauth2/auth?client_id=1234567890.apps.googleusercontent.com&redirect_uri=http%3A//localhost%3A5000/callback&response_type=code&scope=email"

# Act
actual_url = get_google_auth_url()

# Assert
self.assertEqual(actual_url, expected_url)

if __name__ == '__main__':
unittest.main()