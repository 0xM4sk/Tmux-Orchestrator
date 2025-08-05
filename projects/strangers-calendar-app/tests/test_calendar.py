|
import unittest
from backend.api.calendars import get_calendars

class TestCalendarAPI(unittest.TestCase):
def test_get_calendars(self):
response = get_calendars()
self.assertEqual(response.status_code, 200)
data = response.json()
self.assertTrue(len(data) > 0)

if __name__ == '__main__':
unittest.main()