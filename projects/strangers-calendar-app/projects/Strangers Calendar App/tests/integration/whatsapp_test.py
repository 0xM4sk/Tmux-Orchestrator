|
import unittest
from backend.integration.whatsapp import send_whatsapp_message

class TestWhatsApp(unittest.TestCase):
def test_send_whatsapp_message(self):
phone_number = "1234567890"
message = "Hello, this is a test message."
send_whatsapp_message(phone_number, message)
# Add assertions here to verify the message was sent correctly

if __name__ == '__main__':
unittest.main()