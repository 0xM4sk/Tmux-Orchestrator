|
import unittest
from flask import Flask
from backend.auth.apple import apple

class TestAppleOAuth(unittest.TestCase):
def setUp(self):
self.app = Flask(__name__)
self.app.config['TESTING'] = True
self.app.secret_key = 'test-secret-key'
with self.app.app_context():
apple.init_app(self.app)

def test_login_apple(self):
# Simulate the login process
response = self.app.test_client().get('/login/apple')
self.assertEqual(response.status_code, 302)

def test_apple_authorized(self):
# Simulate the authorized callback
token = 'test-access-token'
with self.app.test_request_context():
with patch.object(apple, 'authorize_access_token', return_value={'access_token': token}):
response = self.app.test_client().get('/login/apple/authorized')
self.assertEqual(response.status_code, 200)
self.assertIn('User Info:', response.data.decode())

if __name__ == '__main__':
unittest.main()