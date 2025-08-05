|
# Test suite for phone number and WhatsApp authentication
import pytest
from backend.auth.phone_whatsapp import app

@pytest.fixture
def client():
with app.test_client() as client:
yield client

def test_auth_phone_success(client):
response = client.post('/auth/phone', json={'phone_number': '1234567890'})
assert response.status_code == 200
assert response.json['message'] == 'Phone number authenticated successfully'

def test_auth_phone_failure(client):
response = client.post('/auth/phone')
assert response.status_code == 400
assert response.json['error'] == 'Phone number is required'

def test_auth_whatsapp_success(client):
response = client.post('/auth/whatsapp', json={'whatsapp_token': 'abc123'})
assert response.status_code == 200
assert response.json['message'] == 'WhatsApp token authenticated successfully'

def test_auth_whatsapp_failure(client):
response = client.post('/auth/whatsapp')
assert response.status_code == 400
assert response.json['error'] == 'WhatsApp token is required'