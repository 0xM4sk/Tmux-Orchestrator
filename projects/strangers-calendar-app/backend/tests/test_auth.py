|
# backend/tests/test_auth.py

import pytest
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/auth/login', methods=['POST'])
def login():
# Mock login logic
return "Login Successful"

@pytest.fixture
def client():
app.config['TESTING'] = True
with app.test_client() as client:
yield client

def test_login(client):
response = client.post('/auth/login', json={'username': 'testuser', 'password': 'testpass'})
assert response.status_code == 200
assert b"Login Successful" in response.data