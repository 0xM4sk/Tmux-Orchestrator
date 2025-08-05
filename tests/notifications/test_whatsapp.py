|
import pytest
from backend.notifications.whatsapp import send_whatsapp_message

@pytest.mark.parametrize("phone_number, message", [
("1234567890", "Hello, this is a test message."),
("9876543210", "This is another test message.")
])
def test_send_whatsapp_message(phone_number, message):
response = send_whatsapp_message(phone_number, message)
assert response["status"] == "success"