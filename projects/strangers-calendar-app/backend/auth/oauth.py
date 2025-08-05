|
from flask import Blueprint, redirect, url_for, request
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
google = oauth.register(
name='google',
client_id='YOUR_GOOGLE_CLIENT_ID',
client_secret='YOUR_GOOGLE_CLIENT_SECRET',
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_params=None,
authorize_url='https://accounts.google.com/o/oauth2/auth',
authorize_params=None,
api_base_url='https://www.googleapis.com/oauth2/v1/',
client_kwargs={'scope': 'openid email profile'},
)

oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/login')
def login():
redirect_uri = url_for('oauth.authorize_access_token', _external=True)
return google.authorize_redirect(redirect_uri)

@oauth_bp.route('/authorize-access-token')
def authorize_access_token():
token_response = google.authorize_access_token()
resp = google.get('userinfo')
user_info = resp.json()
# Handle the user information
return redirect(url_for('index'))

oauth_bp.register_blueprint(oauth_bp)