|
import unittest
from flask import Flask, session
from backend.auth.oauth import google_auth, apple_auth

class TestOAuth(unittest.TestCase):
def setUp(self):
app = Flask(__name__)
app.config['TESTING'] = True
self.app = app.test_client()

def test_google_auth(self):
# Placeholder test for Google auth
response = self.app.get('/auth/google')
self.assertEqual(response.status_code, 200)

def test_apple_auth(self):
# Placeholder test for Apple auth
response = self.app.get('/auth/apple')
self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
unittest.main()