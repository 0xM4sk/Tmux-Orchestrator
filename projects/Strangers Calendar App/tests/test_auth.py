|
import requests
from app import app

def test_google_auth_route():
response = requests.get('http://localhost:3000/auth/google')
assert response.status_code == 200