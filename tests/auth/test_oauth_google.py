|
import unittest
from app import create_app, db

class OauthGoogleTestCase(unittest.TestCase):
def setUp(self):
self.app = create_app('testing')
self.app_context = self.app.app_context()
self.app_context.push()
db.create_all()

def tearDown(self):
db.session.remove()
db.drop_all()
self.app_context.pop()

def test_oauth_google_invalid_token(self):
# Simulate a request with an invalid token
response = self.client.post('/auth/google', json={"token": "invalid_token"})

# Assert that the response status code is 401 (Unauthorized)
self.assertEqual(response.status_code, 401)

# Assert that an error message is returned
self.assertIn("Invalid token", response.json["message"])