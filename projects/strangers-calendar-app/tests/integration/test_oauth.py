|
import unittest
from backend.auth.oauth import app

class TestOAuthIntegration(unittest.TestCase):
def setUp(self):
self.app = app.test_client()

def test_google_login_route(self):
response = self.app.get('/login/google')
self.assertEqual(response.status_code, 302)
self.assertIn('https://accounts.google.com/o/oauth2/auth', response.location)

def test_apple_login_route(self):
response = self.app.get('/login/apple')
self.assertEqual(response.status_code, 302)
self.assertIn('https://appleid.apple.com/auth/authorize', response.location)

def test_google_auth_route_error(self):
# Simulate an error in the Google auth route
with app.test_request_context(path='/login/google/auth'):
response = app.dispatch_request()
self.assertEqual(response.status_code, 400)

def test_apple_auth_route_error(self):
# Simulate an error in the Apple auth route
with app.test_request_context(path='/login/apple/auth'):
response = app.dispatch_request()
self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
unittest.main()