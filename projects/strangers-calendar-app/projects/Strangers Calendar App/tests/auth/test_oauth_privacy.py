|
import unittest
from flask import Flask, request, redirect
from backend.auth.oauth import oauth

class TestOAuthPrivacy(unittest.TestCase):
def setUp(self):
self.app = Flask(__name__)
oauth.init_app(self.app)
with self.app.test_client() as client:
self.client = client

def test_privacy_policy_retrieval(self):
response = self.client.get('/auth/privacy')
self.assertEqual(response.status_code, 200)
self.assertIn('Privacy Policy', response.data)

def test_user_data_protection(self):
response = self.client.post('/auth/user/data', json={'user_id': '123'})
self.assertEqual(response.status_code, 200)
self.assertIn('User data protected', response.data)

if __name__ == '__main__':
unittest.main()