|
import pytest
from backend.integration.twilio import send_whatsapp_message, send_sms_message

@pytest.mark.parametrize("to_number, message", [
("+1234567890", "Hello, this is a test message."),
("123-456-7890", "This is an SMS test message.")
])
def test_send_message(to_number, message):
"""
Test the send_message function.
"""
result = send_message(to_number, message)
assert result is not None