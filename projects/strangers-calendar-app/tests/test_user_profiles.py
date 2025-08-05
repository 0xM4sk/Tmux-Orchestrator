|
import unittest
from backend.user import UserProfile

class TestUserProfile(unittest.TestCase):
def test_create_profile(self):
user_profile = UserProfile()
result = user_profile.create("user@example.com", "password123")
self.assertTrue(result)

if __name__ == '__main__':
unittest.main()