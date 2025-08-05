|
# User profile tests
import unittest
from backend.user_profiles import get_user_profile

class TestUserProfiles(unittest.TestCase):
def test_get_user_profile_success(self):
self.assertIsNotNone(get_user_profile('user_id'))

def test_get_user_profile_failure(self):
self.assertIsNone(get_user_profile('non_existent_user_id'))

if __name__ == '__main__':
unittest.main()