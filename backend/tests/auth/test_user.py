|
import unittest
from backend.auth.user import app

class TestUserAuth(unittest.TestCase):
def test_register_user_with_oauth(self):
client = app.test_client()
response = client.post('/register', json={'username': 'testuser', 'password': 'testpass', 'oauth_token': 'valid_oauth_token'})
self.assertEqual(response.status_code, 201)

def test_login_user_with_oauth(self):
client = app.test_client()
response = client.post('/login', json={'username': 'testuser', 'password': 'testpass', 'oauth_token': 'valid_oauth_token'})
self.assertEqual(response.status_code, 200)
