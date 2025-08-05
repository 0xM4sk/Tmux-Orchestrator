|
import unittest
from phone import validate_phone_number

class TestPhoneNumberIntegration(unittest.TestCase):
def test_validate_phone_number_success(self):
is_valid = validate_phone_number('1234567890')
self.assertTrue(is_valid)

def test_validate_phone_number_failure(self):
is_valid = validate_phone_number('123456789')
self.assertFalse(is_valid)