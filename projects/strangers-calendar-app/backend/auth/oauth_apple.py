|
from flask import Flask, request, redirect, url_for, session
from flask_oauthlib.client import OAuth

app = Flask(__name__)
oauth = OAuth(app)
apple = oauth.remote_app('apple',
consumer_key=None,
consumer_secret=None,
request_token_params={},
base_url='https://appleid.apple.com/auth/',
request_token_url=None,
access_token_method='POST',
access_token_url='https://appleid.apple.com/auth/token',
authorize_url='https://appleid.apple.com/auth/authorize')

@app.route('/login/apple')
def login_apple():
return apple.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
resp = apple.authorized_response()
if resp is None or resp.get('access_token') is None:
return 'Access denied: reason={0} error={1}'.format(
request.args['error_reason'],
request.args['error_description']
)
session['apple_token'] = (resp['access_token'], '')
me = apple.get('userinfo')
print(me.data)
return 'You were signed in as: ' + me.data['email']

@apple.tokengetter
def get_apple_oauth_token():
return session.get('apple_token')