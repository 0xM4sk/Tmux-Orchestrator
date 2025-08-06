|
import pytest
from flask import Flask, request, redirect
from backend.auth.oauth import OAuthAuthenticator

# Mock Flask app and OAuthAuthenticator for testing
app = Flask(__name__)
auth = OAuthAuthenticator()

@app.route('/login')
def login():
return auth.login(request.args.get('provider'))

@app.route('/callback/<provider>')
def callback(provider):
return auth.callback(provider, request.args)

def test_login_with_google():
with app.test_request_context('/login?provider=google'):
response = login()
assert response.status_code == 302
assert 'https://accounts.google.com/o/oauth2/auth' in response.location

def test_callback_with_google():
with app.test_request_context('/callback/google?code=some-code&state=some-state'):
response = callback('google')
assert response.status_code == 200
assert 'Logged in successfully' in response.data.decode()

def test_login_with_apple():
with app.test_request_context('/login?provider=apple'):
response = login()
assert response.status_code == 302
assert 'https://appleid.apple.com/auth/authorize' in response.location

def test_callback_with_apple():
with app.test_request_context('/callback/apple?code=some-code&state=some-state'):
response = callback('apple')
assert response.status_code == 200
assert 'Logged in successfully' in response.data.decode()