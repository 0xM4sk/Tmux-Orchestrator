|
import unittest
from backend.auth.apple import apple_login

class TestAppleAuth(unittest.TestCase):
def test_apple_login_success(self):
# Mock request with a valid token
mock_request = {
'headers': {
'Authorization': 'valid_token'
}
}

response = apple_login(mock_request)
self.assertEqual(response, ('User authenticated successfully', 200))

def test_apple_login_failure(self):
# Mock request with an invalid token
mock_request = {
'headers': {
'Authorization': 'invalid_token'
}
}

response = apple_login(mock_request)
self.assertEqual(response, ('Authentication failed', 403))