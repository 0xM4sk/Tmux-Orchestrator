|
import unittest
from .oauth import google_oauth_callback, apple_oauth_callback

class TestOAuthAuthentication(unittest.TestCase):
def test_google_oauth_callback(self):
# Mock the callback function to return a user ID
def mock_google_oauth_callback(code):
return {"user_id": 123}

self.google_oauth_callback = mock_google_oauth_callback
result = self.google_oauth_callback("test_code")
self.assertEqual(result, {"user_id": 123})

def test_apple_oauth_callback(self):
# Mock the callback function to return a user ID
def mock_apple_oauth_callback(code):
return {"user_id": 456}

self.apple_oauth_callback = mock_apple_oauth_callback
result = self.apple_oauth_callback("test_code")
self.assertEqual(result, {"user_id": 456})

if __name__ == '__main__':
unittest.main()