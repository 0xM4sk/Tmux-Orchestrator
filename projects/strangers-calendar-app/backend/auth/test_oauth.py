|
import os
from unittest.mock import patch, MagicMock
from backend.auth.oauth import get_google_oauth_token, get_google_user_info

def test_get_google_oauth_token():
with patch('requests.post') as mock_post:
mock_response = MagicMock()
mock_response.json.return_value = {'access_token': 'fake_access_token'}
mock_post.return_value = mock_response
token = get_google_oauth_token('fake_code')
assert token == {'access_token': 'fake_access_token'}

def test_get_google_user_info():
with patch('requests.get') as mock_get:
mock_response = MagicMock()
mock_response.json.return_value = {'id': '123', 'email': 'test@example.com'}
mock_get.return_value = mock_response
user_info = get_google_user_info('fake_access_token')
assert user_info == {'id': '123', 'email': 'test@example.com'}

if __name__ == '__main__':
import unittest
unittest.main()