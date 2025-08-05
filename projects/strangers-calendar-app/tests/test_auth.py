|
import unittest
from backend.auth.oauth import app

class TestOAuthEndpoints(unittest.TestCase):
def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_google_login(self):
response = self.app.get('/auth/google')
self.assertEqual(response.status_code, 200)

def test_apple_login(self):
response = self.app.get('/auth/apple')
self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
unittest.main()