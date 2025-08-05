|
import unittest
from app.backend.auth.oauth import app

class TestOAuth(unittest.TestCase):
def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_google_auth(self):
response = self.app.get('/auth/google')
self.assertEqual(response.status_code, 302)
self.assertIn('accounts.google.com', response.location)

def test_google_auth_callback(self):
# Mock the Google callback with a valid code
code = 'valid_code'
response = self.app.get(f'/auth/google/callback?code={code}')
self.assertEqual(response.status_code, 200)
self.assertIn('Google User:', response.data.decode())

def test_apple_auth(self):
response = self.app.get('/auth/apple')
self.assertEqual(response.status_code, 302)
self.assertIn('appleid.apple.com', response.location)

def test_apple_auth_callback(self):
# Mock the Apple callback with a valid code
code = 'valid_code'
response = self.app.get(f'/auth/apple/callback?code={code}')
self.assertEqual(response.status_code, 200)
self.assertIn('Apple User:', response.data.decode())

if __name__ == '__main__':
unittest.main()