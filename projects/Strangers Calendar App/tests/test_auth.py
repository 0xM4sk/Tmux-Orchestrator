|
# tests/test_auth.py

import pytest
from your_project.app import create_app  # Adjust this to your actual app creation function

@pytest.fixture
def client():
app = create_app()  # Adjust this to your actual app creation function
app.config['TESTING'] = True
with app.test_client() as client:
yield client

def test_register_user(client):
"""Test user registration endpoint"""
response = client.post('/auth/register', json={'username': 'newuser', 'password': 'newpass'})
assert response.status_code == 201
data = response.get_json()
assert 'username' in data
assert 'password' in data

def test_login_user(client):
"""Test user login endpoint"""
client.post('/auth/register', json={'username': 'testuser', 'password': 'testpass'})
response = client.post('/auth/login', json={'username': 'testuser', 'password': 'testpass'})
assert response.status_code == 200
data = response.get_json()
assert 'message' in data and data['message'] == 'Login successful'