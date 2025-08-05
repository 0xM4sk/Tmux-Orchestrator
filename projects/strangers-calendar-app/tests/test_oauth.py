|
import unittest
from backend.auth.oauth import app

class TestOAuth(unittest.TestCase):
def test_google_auth(self):
with app.test_client() as client:
response = client.get('/auth/google')
self.assertEqual(response.status_code, 200)
self.assertEqual(response.data.decode('utf-8'), 'Google Auth')

def test_apple_auth(self):
with app.test_client() as client:
response = client.get('/auth/apple')
self.assertEqual(response.status_code, 200)
self.assertEqual(response.data.decode('utf-8'), 'Apple Auth')
