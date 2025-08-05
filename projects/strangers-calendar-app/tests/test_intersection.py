|
import unittest
from backend.availability.intersection import intersect_availability

class TestIntersection(unittest.TestCase):
def test_intersect_availability(self):
user1 = {'start': '09:00', 'end': '18:00'}
user2 = {'start': '10:00', 'end': '17:00'}
intersection = intersect_availability(user1, user2)
self.assertEqual(intersection['start'], '10:00')
self.assertEqual(intersection['end'], '17:00')

if __name__ == '__main__':
unittest.main()