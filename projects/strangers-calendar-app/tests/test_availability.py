|
import unittest
from backend.availability.input_storage import store_availability, get_availability

class TestAvailability(unittest.TestCase):
def test_store_availability(self):
response = store_availability('user123', {'start': '09:00', 'end': '18:00'})
self.assertEqual(response, "Availability stored for user user123")

def test_get_availability(self):
availability = get_availability('user123')
self.assertIn('start', availability)
self.assertIn('end', availability)

if __name__ == '__main__':
unittest.main()