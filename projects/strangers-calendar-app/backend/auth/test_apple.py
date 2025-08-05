|
# Test cases for Apple OAuth authentication
import pytest
from httpretty import httprettify, when
from backend.auth.apple import apple_oauth, apple_oauth_callback

@httprettify
def test_apple_oauth():
# Mock the Apple authorization page redirect
httprettify()
with app.test_request_context('/oauth/apple'):
response = app.full_dispatch_request()
assert response.status_code == 302
assert 'https://appleid.apple.com/auth/authorize' in response.location

@httprettify
def test_apple_oauth_callback():
# Mock the token request and user info retrieval
httprettify()
token_response = '{"access_token": "mock_access_token"}'
when(requests.post).with_args(
'https://appleid.apple.com/auth/token',
data={'code': 'mock_code', 'client_id': 'your_apple_client_id', 'client_secret': 'your_apple_client_secret', 'grant_type': 'authorization_code'}
).responds_with(token_response, status=200)
user_info_response = '{"email": "test@example.com"}'
when(requests.get).with_args(
'https://appleid.apple.com/auth/userinfo',
headers={'Authorization': 'Bearer mock_access_token'}
).responds_with(user_info_response, status=200)

with app.test_request_context('/oauth/callback?code=mock_code'):
response = app.full_dispatch_request()
assert response.status_code == 200
assert b"User: test@example.com" in response.data
