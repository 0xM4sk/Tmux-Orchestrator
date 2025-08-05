|
import unittest
from .user_service import send_email

class TestEmailService(unittest.TestCase):
def test_send_email(self):
# Mock the mail.send function
with patch('backend.services.user_service.mail.send') as mock_mail:
send_email("Test Subject", "test@example.com", ["test@example.com"], "Hello, this is a test email.")

# Assert that mail.send was called once with the correct arguments
mock_mail.assert_called_once_with(Message(subject="Test Subject", sender="noreply@example.com", recipients=["test@example.com"], body="Hello, this is a test email."))