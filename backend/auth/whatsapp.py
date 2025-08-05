|
import requests

def send_whatsapp_message(phone_number, message):
url = "https://api.whatsapp.com/send"
params = {
'phone': phone_number,
'message': message,
'token': YOUR_WHATSAPP_TOKEN
}
response = requests.get(url, params=params)
return response.json()