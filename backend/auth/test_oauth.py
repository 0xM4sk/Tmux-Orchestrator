|
import pytest
from backend.auth.oauth import app

@pytest.fixture
def client():
with app.test_client() as client:
yield client

def test_google_auth(client):
response = client.get('/auth/google')
assert response.status_code == 302

def test_google_callback(client, monkeypatch):
# Mock the requests.post call
token_url = 'https://oauth2.googleapis.com/token'
data = {
'client_id': 'your_client_id',
'client_secret': 'your_client_secret',
'redirect_uri': 'http://localhost:5000/auth/callback',
'code': 'test_code',
'grant_type': 'authorization_code'
}
response_data = {'access_token': 'test_access_token'}
monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: type('Response', (), {'json': lambda self: response_data})())

user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
headers = {
'Authorization': f'Bearer {response_data["access_token"]}'
}
user_info_response = requests.get(user_info_url, headers=headers).json()
user_info_expected = {'sub': 'test_user_id', 'name': 'Test User', 'email': 'test@example.com'}

response = client.get('/auth/callback', query_string={'code': 'test_code'})
assert response.status_code == 200
assert response.data.decode('utf-8') == f"User info: {user_info_expected}"