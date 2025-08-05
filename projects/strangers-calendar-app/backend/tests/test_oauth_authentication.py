|
import unittest
from oauth import authenticate_user

class TestOAuthAuthentication(unittest.TestCase):
def test_authenticate_user_success(self):
user = authenticate_user('testuser', 'testpassword')
self.assertIsNotNone(user)

def test_authenticate_user_failure(self):
user = authenticate_user('nonexistentuser', 'wrongpassword')
self.assertIsNone(user)