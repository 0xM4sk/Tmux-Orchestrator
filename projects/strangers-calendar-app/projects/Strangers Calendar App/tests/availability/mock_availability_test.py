|
import unittest
from backend.availability.mock_availability import check_availability, book_slot

class TestMockAvailability(unittest.TestCase):
def test_check_availability(self):
user_id = "user123"
start_time = "10:00 AM"
end_time = "11:00 AM"
is_available = check_availability(user_id, start_time, end_time)
self.assertTrue(is_available)

def test_book_slot(self):
user_id = "user123"
start_time = "10:00 AM"
end_time = "11:00 AM"
book_slot(user_id, start_time, end_time)
# Add assertions here to verify the slot was booked correctly

if __name__ == '__main__':
unittest.main()