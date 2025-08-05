|
# Phone number authentication tests
import unittest
from backend.auth.phone_number import authenticate_phone_number

class TestPhoneNumber(unittest.TestCase):
def test_authenticate_phone_number_success(self):
self.assertTrue(authenticate_phone_number('1234567890'))

def test_authenticate_phone_number_failure(self):
self.assertFalse(authenticate_phone_number('invalid_number'))

if __name__ == '__main__':
unittest.main()