|
import pytest
from backend.auth.oauth import get_google_auth_url, exchange_code_for_token

@pytest.fixture
def client():
from backend.app import app
return app.test_client()

def test_get_google_auth_url(client):
response = client.get('/auth/google')
assert response.status_code == 200
assert 'https://accounts.google.com/o/oauth2/auth' in response.json['url']

def test_exchange_code_for_token(client):
# Mock the OAuth request to return a sample token
from unittest.mock import patch
with patch('requests_oauthlib.OAuth2Session.fetch_token') as mock_fetch:
mock_fetch.return_value = {'access_token': 'sample_access_token'}
response = client.post('/auth/google/callback', data={'code': 'mock_code'})
assert response.status_code == 200
assert response.json['token'] == 'sample_access_token'