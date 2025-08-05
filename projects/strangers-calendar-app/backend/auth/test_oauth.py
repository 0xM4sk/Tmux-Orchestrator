|
# Unit tests for OAuth authentication
import unittest
from backend.auth.oauth import app, google

class TestOAuth(unittest.TestCase):
def setUp(self):
app.config['TESTING'] = True
self.app = app.test_client()

def test_google_login(self):
resp = self.app.get('/login/google')
self.assertEqual(resp.status_code, 302)

def test_token_exchange(self):
resp = self.app.post('/token/google', json={'code': 'test_code'})
self.assertEqual(resp.status_code, 400)
self.assertIn('error' in resp.json and resp.json['error'] == 'No code provided')

if __name__ == '__main__':
unittest.main()