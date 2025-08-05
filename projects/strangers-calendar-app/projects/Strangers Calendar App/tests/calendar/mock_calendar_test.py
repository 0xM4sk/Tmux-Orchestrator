|
import unittest
from backend.calendar.mock_calendar import create_calendar, share_calendar

class TestMockCalendar(unittest.TestCase):
def test_create_calendar(self):
user_id = "user123"
calendar = create_calendar(user_id)
self.assertEqual(calendar, f"Calendar-{user_id}")

def test_share_calendar(self):
calendar_id = "Calendar-123"
recipient_id = "user456"
share_calendar(calendar_id, recipient_id)
# Add assertions here to verify the calendar was shared correctly

if __name__ == '__main__':
unittest.main()