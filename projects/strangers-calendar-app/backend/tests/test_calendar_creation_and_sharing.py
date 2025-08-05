|
import unittest
from calendar_module import create_calendar, share_calendar

class TestCalendarCreationAndSharing(unittest.TestCase):
def test_create_calendar_success(self):
calendar_data = {'title': 'Test Calendar', 'events': []}
result = create_calendar(calendar_data)
self.assertTrue(result)

def test_share_calendar_success(self):
user_id = 1
calendar_id = 1
result = share_calendar(user_id, calendar_id)
self.assertTrue(result)