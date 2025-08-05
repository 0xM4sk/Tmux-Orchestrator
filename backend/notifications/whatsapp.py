|
# WhatsApp notification implementation
import requests

def send_whatsapp_message(phone_number, message):
url = "https://graph.facebook.com/v15.0/me/messages"
headers = {
"Authorization": "Bearer YOUR_ACCESS_TOKEN",
"Content-Type": "application/json"
}
payload = {
"messaging_product": "whatsapp",
"to": phone_number,
"type": "text",
"text": {
"body": message
}
}
response = requests.post(url, headers=headers, json=payload)
return response.json()