|
# Apple OAuth authentication implementation
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route('/auth/apple')
def apple_auth():
url = 'https://appleid.apple.com/auth/authorize'
params = {
'client_id': 'your_client_id',
'redirect_uri': 'http://localhost:5000/auth/callback',
'response_type': 'code id_token',
'scope': 'name email',
'nonce': 'random_nonce',
'state': 'random_state'
}
return redirect(url + '?' + urllib.parse.urlencode(params))

@app.route('/auth/callback')
def apple_callback():
code = request.args.get('code')
state = request.args.get('state')

# Verify the state to prevent CSRF attacks
if state != 'random_state':
return "Invalid state", 400

token_url = 'https://appleid.apple.com/auth/token'
data = {
'client_id': 'your_client_id',
'client_secret': 'your_client_secret',
'redirect_uri': 'http://localhost:5000/auth/callback',
'code': code,
'grant_type': 'authorization_code'
}
response = requests.post(token_url, data=data)
tokens = response.json()
id_token = tokens['id_token']
user_info_url = 'https://appleid.apple.com/auth/authorize?response_type=id_token&client_id=your_client_id&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fauth%2Fcallback'
headers = {
'Authorization': f'Bearer {id_token}'
}
user_info = requests.get(user_info_url, headers=headers).json()
return f"User info: {user_info}"