|
# OAuth authentication implementation
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

# Google OAuth2 endpoint
@app.route('/auth/google')
def google_auth():
# Redirect to Google's authorization server
return redirect('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri=http%3A//localhost:5000/auth/google/callback')

@app.route('/auth/google/callback')
def google_auth_callback():
# Handle the callback from Google
code = request.args.get('code')
token_url = 'https://oauth2.googleapis.com/token'
data = {
'code': code,
'client_id': 'YOUR_GOOGLE_CLIENT_ID',
'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
'redirect_uri': 'http://localhost:5000/auth/google/callback',
'grant_type': 'authorization_code'
}
response = requests.post(token_url, data=data)
access_token = response.json().get('access_token')
# Use the access token to get user information
user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token
user_info_response = requests.get(user_info_url)
user_info = user_info_response.json()
return f'Google User: {user_info}'

# Apple OAuth2 endpoint
@app.route('/auth/apple')
def apple_auth():
# Redirect to Apple's authorization server
return redirect('https://appleid.apple.com/auth/authorize?response_type=code&client_id=YOUR_APPLE_CLIENT_ID&redirect_uri=http%3A//localhost:5000/auth/apple/callback')

@app.route('/auth/apple/callback')
def apple_auth_callback():
# Handle the callback from Apple
code = request.args.get('code')
token_url = 'https://appleid.apple.com/auth/token'
data = {
'grant_type': 'authorization_code',
'client_id': 'YOUR_APPLE_CLIENT_ID',
'redirect_uri': 'http://localhost:5000/auth/apple/callback',
'code_verifier': 'YOUR_CODE_VERIFIER',  # If using PKCE
'code_challenge_method': 'S256'
}
response = requests.post(token_url, data=data)
access_token = response.json().get('access_token')
# Use the access token to get user information
user_info_url = 'https://appleid.apple.com/auth/me?access_token=' + access_token
user_info_response = requests.get(user_info_url)
user_info = user_info_response.json()
return f'Apple User: {user_info}'