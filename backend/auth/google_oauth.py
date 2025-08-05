|
# Google OAuth authentication implementation
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route('/google/login')
def google_login():
# Redirect to Google's authorization page
return redirect('https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5000/google/callback&response_type=code')

@app.route('/google/callback')
def google_callback():
code = request.args.get('code')
# Exchange the authorization code for an access token
response = requests.post('https://oauth2.googleapis.com/token', data={
'code': code,
'client_id': 'YOUR_CLIENT_ID',
'client_secret': 'YOUR_CLIENT_SECRET',
'redirect_uri': 'http://localhost:5000/google/callback',
'grant_type': 'authorization_code'
})
access_token = response.json().get('access_token')
return f'Access token: {access_token}'