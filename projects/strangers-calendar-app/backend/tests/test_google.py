|
import requests
from backend.auth.google import google_login

def test_google_login():
# Simulate the login request and check if it redirects correctly
response = requests.get("http://localhost:5000/login/google")
assert response.status_code == 302
assert "https://accounts.google.com/o/oauth2/auth" in response.headers['Location']