|
import unittest
from backend.user.mock_user import register_user, login_user

class TestMockUser(unittest.TestCase):
def test_register_user(self):
username = "newuser"
password = "password123"
user_id = register_user(username, password)
self.assertEqual(user_id, f"User-{username}")

def test_login_user(self):
username = "admin"
password = "admin"
is_logged_in = login_user(username, password)
self.assertTrue(is_logged_in)

if __name__ == '__main__':
unittest.main()