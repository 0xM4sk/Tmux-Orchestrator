|
import unittest
from app import app, validate_phone_number, send_whatsapp_message

class TestApp(unittest.TestCase):

def setUp(self):
self.app = app.test_client()
self.app.testing = True

def test_validate_phone_number(self):
valid_numbers = ["+1234567890", "+1-123-456-7890", "1234567890"]
invalid_numbers = ["12345", "abcde", "+123-456"]

for number in valid_numbers:
self.assertTrue(validate_phone_number(number))

for number in invalid_numbers:
self.assertFalse(validate_phone_number(number))

def test_send_whatsapp_message(self):
phone_number = "+1234567890"
message = "Test message"
response = send_whatsapp_message(phone_number, message)
# Add assertions to check the response
pass

if __name__ == '__main__':
unittest.main()