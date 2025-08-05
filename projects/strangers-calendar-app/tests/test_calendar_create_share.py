|
import unittest
from backend.calendar.create_share import CalendarManager

class TestCalendarCreateShare(unittest.TestCase):
def setUp(self):
self.manager = CalendarManager()

def test_create_calendar(self):
result = self.manager.create_calendar("user1", {"title": "Work", "date": "2023-10-05"})
self.assertEqual(result, "Calendar created for user1")

def test_share_calendar(self):
self.manager.create_calendar("user1", {"title": "Work", "date": "2023-10-05"})
result = self.manager.share_calendar("user1", 0, "user2")
self.assertEqual(result, "Calendar shared to user2")

def test_share_nonexistent_user(self):
result = self.manager.share_calendar("user1", 0, "user2")
self.assertEqual(result, "User or calendar does not exist")

def test_share_nonexistent_calendar(self):
result = self.manager.share_calendar("user1", 1, "user2")
self.assertEqual(result, "User or calendar does not exist")

if __name__ == '__main__':
unittest.main()