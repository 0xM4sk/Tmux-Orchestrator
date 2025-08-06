|
# Test cases for OAuth privacy compliance
import unittest
from backend.auth.oauth import privacy_compliance

class TestOAuthPrivacy(unittest.TestCase):
def test_privacy_compliance(self):
self.assertTrue(privacy_compliance())