|
import unittest
from backend.auth.google_oauth import app

class TestGoogleOauth(unittest.TestCase):
def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_login_route(self):
response = self.app.get('/login')
self.assertEqual(response.status_code, 302)

def test_authorize_route(self):
with app.test_request_context():
session['google_token'] = 'fake_access_token'
response = self.app.get('/authorize')
self.assertIn('Logged in as', response.data.decode())

if __name__ == '__main__':
unittest.main()