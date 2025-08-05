import pytest
from apple_oauth import apple_oauth, get_apple_access_token

@pytest.fixture
def client():
app.config['TESTING'] = True
with app.test_client() as client:
yield client

def test_get_apple_access_token_success(mocker):
"""Test successful fetch of Apple access token."""
mock_response = {
"access_token": "fake-access-token",
"expires_in": 3600,
"token_type": "Bearer"
}
mocker.patch('apple_oauth.requests.post', return_value=mock_response)
assert get_apple_access_token("fake-code") == mock_response

def test_get_apple_access_token_failure(mocker):
"""Test failure in fetching Apple access token."""
mock_response = {
"status_code": 400,
"text": '{"error": "invalid_grant"}'
}
mocker.patch('apple_oauth.requests.post', return_value=mock_response)
with pytest.raises(Exception) as e:
get_apple_access_token("fake-code")
assert str(e.value) == "Failed to fetch Apple access token"

def test_apple_oauth_route_success(client):
"""Test successful Apple OAuth route."""
response = client.post('/apple/oauth', data={'code': 'fake-code'})
assert response.status_code == 200
assert "access_token" in response.json

def test_apple_oauth_route_error(client):
"""Test error handling in Apple OAuth route."""
response = client.post('/apple/oauth', data={'code': 'fake-code'})
assert response.status_code == 500
assert "error" in response.json