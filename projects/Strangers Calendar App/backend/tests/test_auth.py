|
import requests

def test_oauth_google():
response = requests.get('http://localhost:5000/oauth/google')
assert response.status_code == 200

def test_oauth_apple():
response = requests.get('http://localhost:5000/oauth/apple')
assert response.status_code == 200