|
import unittest
from backend.availability.input_storage import AvailabilityStorage
from datetime import datetime, timedelta

class TestAvailabilityInputStorage(unittest.TestCase):
def setUp(self):
self.storage = AvailabilityStorage()

def test_add_availability(self):
user_id = "user123"
start_time = datetime(2023, 10, 1, 9, 0)
end_time = datetime(2023, 10, 1, 17, 0)
self.storage.add_availability(user_id, start_time, end_time)
stored_start, stored_end = self.storage.get_availability(user_id)
self.assertEqual(stored_start, start_time)
self.assertEqual(stored_end, end_time)

def test_update_availability(self):
user_id = "user123"
start_time = datetime(2023, 10, 1, 9, 0)
end_time = datetime(2023, 10, 1, 17, 0)
self.storage.add_availability(user_id, start_time, end_time)

new_start_time = datetime(2023, 10, 1, 8, 0)
new_end_time = datetime(2023, 10, 1, 16, 0)
self.storage.update_availability(user_id, new_start_time, new_end_time)

stored_start, stored_end = self.storage.get_availability(user_id)
self.assertEqual(stored_start, new_start_time)
self.assertEqual(stored_end, new_end_time)

def test_delete_availability(self):
user_id = "user123"
start_time = datetime(2023, 10, 1, 9, 0)
end_time = datetime(2023, 10, 1, 17, 0)
self.storage.add_availability(user_id, start_time, end_time)

self.storage.delete_availability(user_id)
stored_start, stored_end = self.storage.get_availability(user_id)
self.assertIsNone(stored_start)
self.assertIsNone(stored_end)

def test_edge_cases(self):
user_id = "user123"
start_time = datetime(2023, 10, 1, 9, 0)
end_time = datetime(2023, 10, 1, 17, 0)

# Invalid time range
with self.assertRaises(ValueError):
self.storage.add_availability(user_id, start_time, start_time - timedelta(hours=1))

# User ID not found
with self.assertRaises(KeyError):
self.storage.update_availability("unknown_user", start_time, end_time)
with self.assertRaises(KeyError):
self.storage.delete_availability("unknown_user")

if __name__ == '__main__':
unittest.main()