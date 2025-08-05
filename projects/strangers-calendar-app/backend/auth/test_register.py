|
# Tests for user registration with OAuth options
import unittest
from backend.auth.register import app

class TestRegister(unittest.TestCase):
def test_google_oauth_registration(self):
client = app.test_client()
data = {'oauth_type': 'google'}
response = client.post('/register', json=data)
self.assertEqual(response.status_code, 200)
self.assertIn("Google OAuth registration successful", str(response.data))

def test_apple_oauth_registration(self):
client = app.test_client()
data = {'oauth_type': 'apple'}
response = client.post('/register', json=data)
self.assertEqual(response.status_code, 200)
self.assertIn("Apple OAuth registration successful", str(response.data))

if __name__ == '__main__':
unittest.main()