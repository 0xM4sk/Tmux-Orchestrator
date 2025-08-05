|
import unittest
from datetime import datetime, timedelta

class TestCalendarExpirationAndCleanup(unittest.TestCase):
def test_check_calendar_expiry_success(self):
calendar = {'id': 1, 'expiry_date': (datetime.now() + timedelta(days=5)).isoformat()}
result = check_calendar_expiry(calendar)
self.assertFalse(result)

def test_check_calendar_expiry_failure(self):
calendar = {'id': 1, 'expiry_date': (datetime.now() - timedelta(days=5)).isoformat()}
result = check_calendar_expiry(calendar)
self.assertTrue(result)