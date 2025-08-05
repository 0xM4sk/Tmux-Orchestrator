|
import unittest
from app.auth.oauth import authenticate_google, authenticate_apple

class TestOAuthAuthentication(unittest.TestCase):

def test_authenticate_google(self):
# Arrange
user_data = {"id_token": "google_id_token"}

# Act
result = authenticate_google(user_data)

# Assert
self.assertTrue(result)

def test_authenticate_apple(self):
# Arrange
user_data = {"id_token": "apple_id_token"}

# Act
result = authenticate_apple(user_data)

# Assert
self.assertTrue(result)
