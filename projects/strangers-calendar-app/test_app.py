|
import unittest
from app import app, validate_phone_number

class TestApp(unittest.TestCase):
def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_index_route(self):
response = self.app.get('/')
self.assertEqual(response.status_code, 200)
self.assertIn(b'Strangers Calendar', response.data)

def test_google_login_route(self):
response = self.app.get('/login/google')
self.assertEqual(response.status_code, 200)
self.assertIn(b'Login with Google', response.data)

def test_apple_login_route(self):
response = self.app.get('/login/apple?redirect_uri=/callback/apple')
self.assertEqual(response.status_code, 200)
self.assertIn(b'Login with Apple', response.data)

def test_whatsapp_login_route(self):
response = self.app.get('/login/whatsapp?phone_number=1234567890')
self.assertEqual(response.status_code, 200)
self.assertIn(b'WhatsApp Login Successful for 1234567890', response.data)

def test_validate_phone_number(self):
valid_phone = "+1234567890"
invalid_phone = "abcde12345"
self.assertTrue(validate_phone_number(valid_phone))
self.assertFalse(validate_phone_number(invalid_phone))

if __name__ == '__main__':
unittest.main()