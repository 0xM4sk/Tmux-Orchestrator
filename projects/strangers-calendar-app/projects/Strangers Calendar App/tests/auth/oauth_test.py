|
import unittest
from backend.auth.oauth import google_login, apple_login

class TestOAuth(unittest.TestCase):
def test_google_login(self):
response = google_login()
self.assertIn('https://accounts.google.com/o/oauth2/v2/auth', response.location)

def test_apple_login(self):
response = apple_login()
self.assertIn('https://appleid.apple.com/auth/authorize', response.location)

if __name__ == '__main__':
unittest.main()