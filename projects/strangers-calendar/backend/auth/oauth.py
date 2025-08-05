|
from flask import Blueprint, redirect, url_for, request, session
from authlib.integrations.flask_client import OAuth

oauth = Blueprint('oauth', __name__)

# Configuration for Google and Apple OAuth
google_client_id = 'your_google_client_id'
google_client_secret = 'your_google_client_secret'
apple_client_id = 'your_apple_client_id'
apple_client_secret = 'your_apple_client_secret'

oauth.register(
name='google',
client_id=google_client_id,
client_secret=google_client_secret,
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_params=None,
authorize_url='https://accounts.google.com/o/oauth2/auth',
authorize_params=None,
api_base_url='https://www.googleapis.com/oauth2/v1/',
client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
name='apple',
client_id=apple_client_id,
client_secret=apple_client_secret,
access_token_url='https://appleid.apple.com/auth/token',
access_token_params=None,
authorize_url='https://appleid.apple.com/auth/authorize',
authorize_params=None,
api_base_url='https://appleid.apple.com/',
client_kwargs={'scope': 'name email'},
)

@oauth.route('/login')
def login():
redirect_uri = url_for('oauth.authorize', _external=True)
return oauth.google.authorize_redirect(redirect_uri)

@oauth.route('/authorize')
def authorize():
token = oauth.google.authorize_access_token()
resp = oauth.google.get('userinfo')
user_info = resp.json()

# Handle the user information
session['user'] = user_info
return redirect(url_for('index'))

@oauth.route('/apple_login')
def apple_login():
redirect_uri = url_for('oauth.apple_authorize', _external=True)
return oauth.apple.authorize_redirect(redirect_uri)

@oauth.route('/apple_authorize')
def apple_authorize():
token = oauth.apple.authorize_access_token()
resp = oauth.apple.get('userinfo')
user_info = resp.json()

# Handle the user information
session['user'] = user_info
return redirect(url_for('index'))