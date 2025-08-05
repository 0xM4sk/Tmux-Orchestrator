|
import unittest

class TestAvailabilityWindowsInputStorage(unittest.TestCase):
def test_save_availability_window_success(self):
window = {'start_time': '2023-10-01T09:00:00Z', 'end_time': '2023-10-01T17:00:00Z'}
result = save_availability_window(window)
self.assertTrue(result)

def test_load_availability_windows_success(self):
user_id = 1
windows = load_availability_windows(user_id)
self.assertEqual(len(windows), 2)