|
import unittest
from flask import Flask, request
from backend.auth.apple import apple_auth_endpoint

app = Flask(__name__)

@app.route('/apple-auth', methods=['POST'])
def test_route():
return apple_auth_endpoint(request)

class TestAppleAuth(unittest.TestCase):
def test_success_response(self):
# Mock the request and response to simulate a successful Apple auth call
mock_request_data = {'code': 'test_code'}
with app.test_client() as client:
response = client.post('/apple-auth', json=mock_request_data)
result = response.get_json()

# Check if the response is as expected
self.assertEqual(result['access_token'], 'test_token')
self.assertEqual(result['id_token'], 'test_id_token')

if __name__ == '__main__':
unittest.main()