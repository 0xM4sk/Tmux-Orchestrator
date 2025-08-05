|
from flask import Flask, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
from config import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

app = Flask(__name__)
oauth = OAuth(app)
google = oauth.remote_app('google',
consumer_key=GOOGLE_OAUTH_CLIENT_ID,
consumer_secret=GOOGLE_OAUTH_CLIENT_SECRET,
request_token_params={
'scope': 'email'
},
base_url='https://www.googleapis.com/oauth2/v1/',
request_token_url=None,
access_token_method='POST',
access_token_url='https://accounts.google.com/o/oauth2/token',
authorize_url='https://accounts.google.com/o/oauth2/auth')

@app.route('/login/google')
def login_google():
return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
resp = google.authorized_response()
if resp is None or resp.get('access_token') is None:
return 'Access denied: reason={0} error={1}'.format(
request.args['error_reason'],
request.args['error_description']
)
session['google_token'] = (resp['access_token'], '')
me = google.get('userinfo')
print(me.data)
return 'You were signed in as: ' + me.data['email']

@google.tokengetter
def get_google_oauth_token():
return session.get('google_token')