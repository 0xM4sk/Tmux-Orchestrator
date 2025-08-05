|
import unittest
from .OAuthButtons import handle_oauth_response

class TestOAuthButtons(unittest.TestCase):
@patch('backend.auth.OAuthButtons.validate_token')
def test_handle_oauth_response_valid_token(self, mock_validate_token):
# Mock the validate_token function to return True
mock_validate_token.return_value = True

# Call the decorated function with a valid token
response = handle_oauth_response(lambda: {"message": "Authenticated successfully"})()

# Assert that the response status code is 200 and the message is correct
self.assertEqual(response.status_code, 200)
self.assertIn("Authenticated successfully", response.json["message"])

@patch('backend.auth.OAuthButtons.validate_token')
def test_handle_oauth_response_invalid_token(self, mock_validate_token):
# Mock the validate_token function to return False
mock_validate_token.return_value = False

# Call the decorated function with an invalid token
response = handle_oauth_response(lambda: {"message": "Authenticated successfully"})()

# Assert that the response status code is 401 and the message is correct
self.assertEqual(response.status_code, 401)
self.assertIn("Invalid token", response.json["message"])