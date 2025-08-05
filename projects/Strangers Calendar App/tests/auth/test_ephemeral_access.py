|
# Test cases for ephemeral access
import unittest
from projects.Strangers Calendar App.backend.auth.oauth_google import app as google_app
from projects.Strangers Calendar App.backend.auth.oauth_apple import app as apple_app

class TestEphemeralAccess(unittest.TestCase):
def test_google_auth_callback(self):
with google_app.test_client() as client:
response = client.get('/auth/google/callback?code=some_code')
self.assertEqual(response.status_code, 200)
self.assertIn('Access Token', response.data.decode())

def test_apple_auth_callback(self):
with apple_app.test_client() as client:
response = client.get('/auth/apple/callback?code=some_code')
self.assertEqual(response.status_code, 200)
self.assertIn('Access Token', response.data.decode())

if __name__ == '__main__':
unittest.main()