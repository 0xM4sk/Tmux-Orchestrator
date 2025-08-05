|
import unittest
from backend.auth.oauth import app

class TestOAuthEndpoints(unittest.TestCase):
def test_google_auth(self):
with app.test_client() as client:
response = client.get('/auth/google')
self.assertEqual(response.status_code, 200)
self.assertIn('Google Auth Endpoint', response.data.decode())

def test_apple_auth(self):
with app.test_client() as client:
response = client.get('/auth/apple')
self.assertEqual(response.status_code, 200)
self.assertIn('Apple Auth Endpoint', response.data.decode())

if __name__ == '__main__':
unittest.main()