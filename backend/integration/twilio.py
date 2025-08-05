|
# twilio.py

from twilio.rest import Client
from backend.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number, message):
"""
Send a WhatsApp message to the specified phone number.
"""
message = client.messages.create(
body=message,
from_='+1234567890',  # Replace with your Twilio number
to=to_number
)
return message.sid

def send_sms_message(to_number, message):
"""
Send an SMS message to the specified phone number.
"""
message = client.messages.create(
body=message,
from_='+1234567890',  # Replace with your Twilio number
to=to_number
)
return message.sid