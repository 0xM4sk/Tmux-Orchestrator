|
import unittest
from backend.auth.oauth import authenticate_user
from backend.calendars/events import create_event, get_event
from backend.availability/windows import set_availability_window

class TestIntegrationSuite(unittest.TestCase):
def test_oauth_authentication(self):
# Simulate user login and token generation
user_token = authenticate_user('testuser', 'password')
self.assertIsNotNone(user_token)

def test_calendar_events(self):
# Create a calendar event and verify it's accessible
create_event('testuser', 'Meeting with team', '2025-10-01T10:00Z')
event = get_event('testuser', 1)
self.assertIsNotNone(event)

def test_availability_windows(self):
# Set availability window and verify it's saved
set_availability_window('testuser', '2025-08-06T09:00Z', '2025-08-06T17:00Z')
user_availability = get_user_availability('testuser')
self.assertIn(('2025-08-06T09:00Z', '2025-08-06T17:00Z'), user_availability)

if __name__ == '__main__':
unittest.main()