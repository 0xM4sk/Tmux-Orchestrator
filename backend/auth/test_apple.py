|
import pytest
from backend.auth.apple import app

@pytest.fixture
def client():
with app.test_client() as client:
yield client

def test_apple_auth(client):
response = client.get('/auth/apple')
assert response.status_code == 302

def test_apple_callback(client, monkeypatch):
# Mock the requests.post call
token_url = 'https://appleid.apple.com/auth/token'
data = {
'client_id': 'your_client_id',
'client_secret': 'your_client_secret',
'redirect_uri': 'http://localhost:5000/auth/callback',
'code': 'test_code',
'grant_type': 'authorization_code'
}
response_data = {'id_token': 'test_id_token'}
monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: type('Response', (), {'json': lambda self: response_data})())

user_info_url = 'https://appleid.apple.com/auth/authorize?response_type=id_token&client_id=your_client_id&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fauth%2Fcallback'
headers = {
'Authorization': f'Bearer {response_data["id_token"]}'
}
user_info_response = requests.get(user_info_url, headers=headers).json()
user_info_expected = {'sub': 'test_user_id', 'name': 'Test User', 'email': 'test@example.com'}

response = client.get('/auth/callback', query_string={'code': 'test_code', 'state': 'random_state'})
assert response.status_code == 200
assert response.data.decode('utf-8') == f"User info: {user_info_expected}"