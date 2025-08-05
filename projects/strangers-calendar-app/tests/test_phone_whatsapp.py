|
import unittest
from backend.auth.phone_whatsapp import some_function

class TestPhoneWhatsApp(unittest.TestCase):
def test_some_function(self):
result = some_function()
self.assertEqual(result, expected_value)

if __name__ == '__main__':
unittest.main()