|
from twilio.rest import Client

def send_whatsapp_message(to_number, message):
account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
client = Client(account_sid, auth_token)
message = client.messages.create(
body=message,
from_='+15017122661',
to=to_number
)
return message.sid