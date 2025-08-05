|
# backend/tests/auth/test_apple_auth.py

import unittest
from flask import Flask, request
from backend.routes.auth import apple_auth_bp

class TestAppleAuthRoutes(unittest.TestCase):
def setUp(self):
app = Flask(__name__)
app.register_blueprint(apple_auth_bp)
self.app = app.test_client()

def test_apple_login_route(self):
response = self.app.get('/apple/login')
self.assertEqual(response.status_code, 302)  # Redirect status code

def test_apple_callback_route_with_valid_code(self):
with self.app:
with self.app.session_transaction() as sess:
sess['code'] = 'valid_code'  # Mock a valid authorization code
response = self.app.get('/apple/callback')
self.assertEqual(response.status_code, 200)
self.assertIn('User authenticated with Apple', response.data.decode())

def test_apple_callback_route_with_invalid_code(self):
with self.app:
with self.app.session_transaction() as sess:
sess['code'] = None  # Mock an invalid authorization code
response = self.app.get('/apple/callback')
self.assertEqual(response.status_code, 400)
self.assertIn('Error: Code missing', response.data.decode())

if __name__ == '__main__':
unittest.main()