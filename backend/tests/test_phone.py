|
import unittest
from backend.auth.verification import app

class TestPhoneVerification(unittest.TestCase):
def test_verify_phone_success(self):
with app.test_client() as client:
data = {'phone_number': '+1234567890'}
response = client.post('/verify_phone', json=data)
self.assertEqual(response.status_code, 200)
self.assertIn('verification_code', response.json)

def test_verify_phone_missing_phone(self):
with app.test_client() as client:
data = {}
response = client.post('/verify_phone', json=data)
self.assertEqual(response.status_code, 400)
self.assertIn('error', response.json)
self.assertEqual(response.json['error'], 'Phone number is required')

def test_verify_phone_invalid_phone(self):
with app.test_client() as client:
data = {'phone_number': '1234567890'}
response = client.post('/verify_phone', json=data)
self.assertEqual(response.status_code, 400)
self.assertIn('error', response.json)
self.assertEqual(response.json['error'], 'Phone number must start with "+"')

if __name__ == '__main__':
unittest.main()