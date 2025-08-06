|
# Apple OAuth authentication implementation
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

def apple_authenticate():
state = generate_state()
session['state'] = state
auth_url = f'https://appleid.apple.com/auth/authorize?response_type=code&client_id={APPLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email,name&response_mode=form_post&state={state}'
return redirect(auth_url)

def apple_callback():
code = request.form.get('code')
state = request.form.get('state')

if state != session['state']:
abort(403)

token_url = 'https://appleid.apple.com/auth/token'
data = {
'grant_type': 'authorization_code',
'client_id': APPLE_CLIENT_ID,
'redirect_uri': REDIRECT_URI,
'code_verifier': session['code_verifier'],
'code': code
}
response = requests.post(token_url, data=data)
if response.status_code == 200:
tokens = response.json()
return {'access_token': tokens['access_token'], 'refresh_token': tokens['refresh_token']}
else:
abort(500)

@app.route('/apple/auth', methods=['GET'])
def apple_auth():
return apple_authenticate()

@app.route('/apple/callback', methods=['POST'])
def apple_callback_route():
return apple_callback()