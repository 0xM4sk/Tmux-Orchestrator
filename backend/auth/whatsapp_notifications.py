|
# WhatsApp notification implementation using Twilio
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_notification(phone_number, message):
"""Send a WhatsApp notification."""
try:
message = client.messages.create(
body=message,
from_=TWILIO_PHONE_NUMBER,
to=phone_number
)
return {'status': 'success', 'sid': message.sid}
except Exception as e:
return {'status': 'error', 'message': str(e)}