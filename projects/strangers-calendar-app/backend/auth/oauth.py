|
# OAuth authentication implementation
from flask import Flask, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
oauth = OAuth(app)

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

apple = oauth.register(
name='apple',
client_id='YOUR_APPLE_CLIENT_ID',
client_secret=None,
access_token_url='https://appleid.apple.com/auth/token',
access_token_params=None,
authorize_url='https://appleid.apple.com/auth/authorize',
authorize_params=None,
api_base_url='https://appleid.apple.com/',
client_kwargs={'scope': 'name email'},
)

@app.route('/login/google')
def login_google():
redirect_uri = url_for('authorize', _external=True)
return google.authorize_redirect(redirect_uri)

@app.route('/oauth/callback/google')
def authorize():
token = google.authorize_access_token()
resp = google.get('userinfo')
user_info = resp.json()
session['user'] = user_info
return 'Logged in successfully!'

if __name__ == '__main__':
app.run(debug=True)