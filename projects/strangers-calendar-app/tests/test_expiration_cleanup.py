|
import unittest
from backend.calendar.expiration_cleanup import expire_calendar, cleanup_expired_calendars

class TestExpirationCleanup(unittest.TestCase):
def test_expire_calendar(self):
response = expire_calendar('calendar123')
self.assertIn('expired at', response)

def test_cleanup_expired_calendars(self):
response = cleanup_expired_calendars()
self.assertEqual(response, "Expired calendars cleaned up")

if __name__ == '__main__':
unittest.main()