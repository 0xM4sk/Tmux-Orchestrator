|
# tests/test_auth.py

import pytest
from flask import Flask, request
from your_app import create_app  # Adjust this to your actual app creation function

@pytest.fixture
def client():
app = create_app()  # Adjust this to your actual app creation function
app.config['TESTING'] = True
with app.test_client() as client:
yield client

def test_oauth_login(client):
"""Test OAuth login endpoint"""
response = client.post('/auth/login', json={'provider': 'google'})
assert response.status_code == 200

def test_oauth_signup(client):
"""Test OAuth signup endpoint"""
response = client.post('/auth/signup', json={'provider': 'google'})
assert response.status_code == 200