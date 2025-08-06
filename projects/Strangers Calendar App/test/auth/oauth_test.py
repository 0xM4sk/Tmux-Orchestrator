|
import unittest
from backend.auth.oauth import google_auth, apple_auth

class OAuthTests(unittest.TestCase):

def test_google_auth(self):
# Mock the authentication response
mock_response = {"access_token": "mock_token", "id_token": "mock_id_token"}
self.assertEqual(google_auth("mock_code"), mock_response)

def test_apple_auth(self):
# Mock the authentication response
mock_response = {"access_token": "mock_token", "id_token": "mock_id_token"}
self.assertEqual(apple_auth("mock_code"), mock_response)

if __name__ == '__main__':
unittest.main()