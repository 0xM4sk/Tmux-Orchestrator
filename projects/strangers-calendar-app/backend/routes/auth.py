|
from flask import Flask, redirect, url_for, request, session
from oauthlib.oauth2 import WebApplicationClient
from backend.config.oauth import oauth_config

app = Flask(__name__)
client = WebApplicationClient(oauth_config['GOOGLE_CLIENT_ID'])

@app.route('/login')
def login():
# Create URL for request to Google's authorization server
redirect_uri = url_for('authorize', _external=True)
return client.prepare_request_uri(
'https://accounts.google.com/o/oauth2/auth',
redirect_uri=redirect_uri,
scope=['openid', 'email'],
response_type='code')

@app.route('/auth/callback')
def authorize():
# Exchange authorization code for access token
code = request.args.get('code')
token_url, headers, body = client.prepare_token_request(
'https://oauth2.googleapis.com/token',
authorization_response=request.url,
redirect_uri=url_for('authorize', _external=True),
client_secret=oauth_config['GOOGLE_CLIENT_SECRET'],
code=code)
token_response = requests.post(token_url, headers=headers, data=body, auth=(client.client_id, client.client_secret))
client.parse_request_body_response(json.loads(token_response.text))

# Use access token to fetch user info
user_info_url, _, _ = client.add_token('https://www.googleapis.com/oauth2/v1/userinfo')
user_info_response = requests.get(user_info_url)
user_info = json.loads(user_info_response.text)

session['user'] = user_info
return redirect(url_for('index'))

@app.route('/logout')
def logout():
session.pop('user', None)
return redirect(url_for('index'))