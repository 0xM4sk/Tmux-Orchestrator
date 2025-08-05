|
# Test cases for phone number authentication
import pytest

from backend.auth.phone import app, phone_auth

@pytest.fixture(scope='module')
def client():
with app.test_client() as c:
yield c

def test_phone_auth(client):
response = client.get('/auth/phone?phone_number=+1234567890')
assert response.status_code == 200
assert b"Verification code sent to +1234567890" in response.data
