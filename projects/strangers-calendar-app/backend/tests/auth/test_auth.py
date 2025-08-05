|
import unittest
from auth_module import authenticate_user, generate_token

class TestAuth(unittest.TestCase):
def test_authenticate_user(self):
self.assertTrue(authenticate_user('user@example.com', 'password123'))
self.assertFalse(authenticate_user('user@example.com', 'wrong_password'))

def test_generate_token(self):
token = generate_token('user@example.com')
self.assertIsNotNone(token)
self.assertIsInstance(token, str)

if __name__ == '__main__':
unittest.main()