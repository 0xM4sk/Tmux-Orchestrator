|
import unittest

class TestAvailabilityIntersectionAlgorithm(unittest.TestCase):
def test_availability_intersection_success(self):
window1 = {'start_time': '2023-10-01T09:00:00Z', 'end_time': '2023-10-01T17:00:00Z'}
window2 = {'start_time': '2023-10-01T14:00:00Z', 'end_time': '2023-10-01T20:00:00Z'}
intersection = find_availability_intersection(window1, window2)
self.assertEqual(intersection['start_time'], '2023-10-01T14:00:00Z')
self.assertEqual(intersection['end_time'], '2023-10-01T17:00:00Z')