|
import unittest
from flask import Flask, session
from backend.auth.oauth import oauth_bp

class TestOAuth(unittest.TestCase):
def setUp(self):
app = Flask(__name__)
app.config['TESTING'] = True
app.register_blueprint(oauth_bp)
self.app = app.test_client()
self.ctx = app.test_request_context()

def tearDown(self):
session.clear()
with self.ctx:
self.app.reset_context()

def test_login_redirects_to_google_auth_url(self):
response = self.app.get('/login')
self.assertEqual(response.status_code, 302)
self.assertIn('https://accounts.google.com/o/oauth2/auth', response.location)

def test_authorize_access_token_retrieves_user_info(self):
with self.ctx:
with self.app.test_request_context():
session['oauth_token'] = 'test_token'
resp = self.app.get('/authorize-access-token')
self.assertEqual(resp.status_code, 302)
user_info = session.get('user_info', {})
self.assertIn('email', user_info)

if __name__ == '__main__':
unittest.main()