|
# Apple OAuth authentication implementation
from flask import Flask, request, redirect
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
oauth = OAuth(app)

apple = oauth.register(
name='apple',
client_id='your-client-id',
client_secret='your-client-secret',
access_token_url='https://appleid.apple.com/auth/token',
authorize_url='https://appleid.apple.com/auth/authorize',
api_base_url='https://appleid.apple.com/',
client_kwargs={'scope': 'name email'}
)

@app.route('/login/apple')
def login_apple():
redirect_uri = request.base_url + '/authorized'
return apple.authorize_redirect(redirect_uri)

@app.route('/login/apple/authorized')
def apple_authorized():
token = apple.authorize_access_token()
resp = apple.get('userinfo')
user_info = resp.json()

# Handle the user_info here
return f"User Info: {user_info}"