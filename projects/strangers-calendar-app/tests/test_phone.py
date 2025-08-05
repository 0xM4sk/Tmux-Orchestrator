|
import unittest
from backend.auth.phone import validate_phone_number

class TestPhoneValidation(unittest.TestCase):
def test_valid_phone_number(self):
self.assertTrue(validate_phone_number("1234567890")[0])

def test_invalid_phone_number(self):
self.assertFalse(validate_phone_number("abcde1234")[0])
self.assertFalse(validate_phone_number("123456789"))
self.assertFalse(validate_phone_number("12345678901"))

if __name__ == '__main__':
unittest.main()