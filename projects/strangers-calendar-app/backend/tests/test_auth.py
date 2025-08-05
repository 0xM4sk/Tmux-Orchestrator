|
import unittest
from app import app
from flask import request, jsonify

class AuthTestCase(unittest.TestCase):

def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_google_login(self):
response = self.app.post('/auth/login/google', json={'id_token': 'some_google_id_token'})
self.assertEqual(response.status_code, 200)
data = response.get_json()
self.assertIn('access_token', data)

def test_apple_login(self):
response = self.app.post('/auth/login/apple', json={'id_token': 'some_apple_id_token'})
self.assertEqual(response.status_code, 200)
data = response.get_json()
self.assertIn('access_token', data)

if __name__ == '__main__':
unittest.main()