|
# Google OAuth authentication implementation
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route('/auth/google/callback')
def google_auth_callback():
code = request.args.get('code')
token_url = 'https://oauth2.googleapis.com/token'
data = {
'client_id': 'YOUR_GOOGLE_CLIENT_ID',
'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
'redirect_uri': 'http://localhost:5000/auth/google/callback',
'grant_type': 'authorization_code',
'code': code
}
response = requests.post(token_url, data=data)
access_token = response.json().get('access_token')
return f'Access Token: {access_token}'

if __name__ == '__main__':
app.run(debug=True)