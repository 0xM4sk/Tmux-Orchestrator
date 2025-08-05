|
import unittest
from backend.calendars.api import app as calendar_app

class TestCalendarAPI(unittest.TestCase):
def setUp(self):
self.app = calendar_app.test_client()
self.app.testing = True

def test_create_calendar(self):
response = self.app.post('/calendar', json={'name': 'Test Calendar'})
self.assertEqual(response.status_code, 201)
data = response.get_json()
self.assertIn('calendar_id', data)

def test_get_calendar(self):
response = self.app.post('/calendar', json={'name': 'Test Calendar'})
calendar_id = response.get_json()['calendar_id']
response = self.app.get(f'/calendar/{calendar_id}')
self.assertEqual(response.status_code, 200)
data = response.get_json()
self.assertIn('id', data)

if __name__ == '__main__':
unittest.main()