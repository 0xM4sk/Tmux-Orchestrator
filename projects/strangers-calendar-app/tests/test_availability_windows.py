|
# Unit tests for availability windows logic
import unittest
from backend.availability.windows import parse_availability_window, is_window_valid, save_availability_window

class TestAvailabilityWindows(unittest.TestCase):
def test_parse_availability_window(self):
window_str = "2023-10-01 09:00-2023-10-01 10:00"
expected_result = {'start': datetime(2023, 10, 1, 9), 'end': datetime(2023, 10, 1, 10)}
self.assertEqual(parse_availability_window(window_str), expected_result)

def test_is_window_valid(self):
valid_window = {'start': datetime(2023, 10, 1, 9), 'end': datetime(2023, 10, 1, 10)}
invalid_window = {'start': datetime(2023, 10, 1, 10), 'end': datetime(2023, 10, 1, 9)}
self.assertTrue(is_window_valid(valid_window))
self.assertFalse(is_window_valid(invalid_window))

def test_save_availability_window(self):
window_data = {'start': datetime(2023, 10, 1, 9), 'end': datetime(2023, 10, 1, 10)}
save_availability_window(window_data)
# Placeholder assertion to check if the function is called
self.assertTrue(True)

if __name__ == '__main__':
unittest.main()