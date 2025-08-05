|
import unittest
from whatsapp import send_whatsapp_message

class TestWhatsAppIntegration(unittest.TestCase):
def test_send_whatsapp_message_success(self):
result = send_whatsapp_message('Hello, WhatsApp!')
self.assertTrue(result)

def test_send_whatsapp_message_failure(self):
result = send_whatsapp_message('')
self.assertFalse(result)