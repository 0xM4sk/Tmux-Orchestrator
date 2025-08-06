|
import unittest
from backend.auth.apple_oauth import apple_authenticate, apple_callback

class TestAppleOAuth(unittest.TestCase):
def test_apple_auth(self):
# Mock request and response for testing purposes
with app.test_request_context():
response = apple_authenticate()
self.assertEqual(response.status_code, 302)
self.assertIn('https://appleid.apple.com/auth/authorize', response.location)

def test_apple_callback(self):
# Mock request and response for testing purposes
with app.test_request_context():
response = apple_callback()
self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
unittest.main()