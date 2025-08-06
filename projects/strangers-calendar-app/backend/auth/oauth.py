|
# OAuth authentication implementation
from flask import Flask, request, redirect
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
oauth = OAuth(app)

google = oauth.register(
name='google',
client_id='your-google-client-id',
client_secret='your-google-client-secret',
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_params=None,
authorize_url='https://accounts.google.com/o/oauth2/auth',
authorize_params=None,
api_base_url='https://www.googleapis.com/oauth2/v1/',
client_kwargs={'scope': 'openid email profile'},
)

apple = oauth.register(
name='apple',
client_id='your-apple-client-id',
client_secret=jwt.encode({'iss': 'your-team-id', 'aud': 'https://appleid.apple.com/auth/authorization-server', 'exp': time.time() + 86400}, 'your-private-key-file.pem', algorithm='ES256'),
access_token_url='https://appleid.apple.com/auth/token',
access_token_params=None,
authorize_url='https://appleid.apple.com/auth/authorize',
authorize_params=None,
api_base_url='https://api.apple.com/',
client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login-google')
def login_google():
redirect_uri = url_for('authorize', _external=True)
return google.authorize_redirect(redirect_uri)

@app.route('/login-apple')
def login_apple():
redirect_uri = url_for('authorize', _external=True)
return apple.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
token = google.authorize_access_token()
resp = google.get('userinfo')
user_info = resp.json()
# Process user information and log in the user
return f'Logged in as {user_info["email"]}'