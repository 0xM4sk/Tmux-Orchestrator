|
# Apple authentication implementation
from flask import request, redirect, jsonify
from functools import wraps
import requests

def apple_callback():
code = request.args.get('code')
if not code:
return jsonify({'error': 'Missing code'}), 400

token_url = "https://appleid.apple.com/auth/token"
payload = {
'client_id': 'com.example.yourapp',
'client_secret': 'your_client_secret',
'code_verifier': request.args.get('codeVerifier'),
'grant_type': 'authorization_code',
'redirect_uri': request.args.get('redirectUri')
}

response = requests.post(token_url, data=payload)
if response.status_code != 200:
return jsonify({'error': 'Token exchange failed'}), response.status_code

access_token = response.json().get('access_token')
user_info_url = "https://appleid.apple.com/auth/userinfo"
headers = {
'Authorization': f'Bearer {access_token}'
}

user_info_response = requests.get(user_info_url, headers=headers)
if user_info_response.status_code != 200:
return jsonify({'error': 'User info fetch failed'}), user_info_response.status_code

user_info = user_info_response.json()
# Process the user_info and create a user session
return jsonify(user_info)

def apple_auth_required(f):
@wraps(f)
def decorated_function(*args, **kwargs):
if not 'apple_token' in request.headers:
return jsonify({'error': 'Apple token missing'}), 401

# Validate the Apple token here
return f(*args, **kwargs)

return decorated_function