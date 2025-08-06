|
import pytest
from backend.auth.oauth import google_auth_callback, apple_auth_callback

def test_google_auth_callback():
# Mock the OAuth callback response
mock_response = {
'id_token': 'mocked_id_token',
'token_type': 'Bearer'
}
# Call the function and assert the expected outcome
result = google_auth_callback(mock_response)
assert result == "Google Auth Successful"

def test_apple_auth_callback():
# Mock the OAuth callback response
mock_response = {
'id_token': 'mocked_id_token',
'token_type': 'Bearer'
}
# Call the function and assert the expected outcome
result = apple_auth_callback(mock_response)
assert result == "Apple Auth Successful"