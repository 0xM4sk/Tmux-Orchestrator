|
import pytest
from flask import Flask
from backend.auth.apple import apple_callback

def test_apple_callback_with_code():
app = Flask(__name__)
with app.test_client() as client:
response = client.post('/auth/apple/callback', data={'code': 'test_code'})
assert response.status_code == 200
assert 'sub' in response.json()