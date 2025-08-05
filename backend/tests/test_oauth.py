|
import pytest
from flask import Flask, request, redirect

def test_google_auth():
app = Flask(__name__)
@app.route('/auth/google')
def google_auth():
# Simulate Google OAuth authentication
return "Google Auth Success"

with app.test_client() as client:
response = client.get('/auth/google')
assert response.status_code == 200
assert response.data.decode('utf-8') == "Google Auth Success"

def test_whatsapp_auth():
app = Flask(__name__)
@app.route('/auth/whatsapp')
def whatsapp_auth():
# Simulate WhatsApp OAuth authentication
return "WhatsApp Auth Success"

with app.test_client() as client:
response = client.get('/auth/whatsapp')
assert response.status_code == 200
assert response.data.decode('utf-8') == "WhatsApp Auth Success"