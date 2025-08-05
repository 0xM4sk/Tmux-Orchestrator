|
import unittest
from unittest.mock import patch
from backend.auth.oauth import google_login, apple_callback

class TestOAuthIntegration(unittest.TestCase):
@patch('backend.auth.oauth.requests.post')
def test_google_login(self, mock_post):
# Mock the response from Google's OAuth API
mock_response = {'access_token': 'mock_token'}
mock_post.return_value.json.return_value = mock_response

result = google_login('fake_code')
self.assertEqual(result, mock_response)

@patch('backend.auth.oauth.requests.post')
def test_apple_callback(self, mock_post):
# Mock the response from Apple's OAuth API
mock_response = {'access_token': 'mock_token'}
mock_post.return_value.json.return_value = mock_response

result = apple_callback('fake_code')
self.assertEqual(result, mock_response)

if __name__ == '__main__':
unittest.main()