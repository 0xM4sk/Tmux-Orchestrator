|
import pytest
from flask import Flask, request, redirect
from backend.auth.oauth import authenticate_google, authenticate_apple

@pytest.fixture(scope="module")
def app():
app = Flask(__name__)
return app

def test_oauth_google(app):
with app.test_client() as client:
response = client.get('/auth/google')
assert response.status_code == 302
assert 'https://accounts.google.com/o/oauth2/auth' in response.location

def test_oauth_apple(app):
with app.test_client() as client:
response = client.get('/auth/apple')
assert response.status_code == 302
assert 'https://appleid.apple.com/auth/authorize' in response.location