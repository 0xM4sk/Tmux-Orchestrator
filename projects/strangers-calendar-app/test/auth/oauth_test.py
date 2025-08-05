|
import unittest
from backend.auth.oauth import app

class TestOAuth(unittest.TestCase):

def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_google_login(self):
response = self.app.get('/login/google')
self.assertEqual(response.status_code, 200)
self.assertIn("Google Login", response.data.decode())

def test_apple_login(self):
response = self.app.get('/login/apple')
self.assertEqual(response.status_code, 200)
self.assertIn("Apple Login", response.data.decode())