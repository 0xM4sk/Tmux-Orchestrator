|
# Comprehensive integration test
from backend.auth.oauth import google_login, apple_login
from backend.calendars import Calendar
from backend.availability import Availability
from backend.intersection import intersect_availability
from backend.cleanup import expire_calendars

def test_oauth_authentication():
assert google_login() == 'https://accounts.google.com/o/oauth2/v2/auth'
assert apple_login() == 'https://appleid.apple.com/auth/authorize'

def test_calendar_creation_and_sharing():
calendar = Calendar(owner='user1')
calendar.add_event('Meeting', datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=1))
assert calendar.share_with('user2') == 'Calendar shared with user2'

def test_availability_windows_input_and_storage():
availability = Availability(user='user1')
availability.add_window(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=1))
assert availability.get_windows() == [(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=1))]

def test_availability_intersection_algorithm():
availability1 = Availability(user='user1')
availability2 = Availability(user='user2')
availability1.add_window(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=1))
availability2.add_window(datetime.datetime.now() + datetime.timedelta(hours=0.5), datetime.datetime.now() + datetime.timedelta(hours=1.5))
assert intersect_availability(availability1.windows, availability2.windows) == [(datetime.datetime.now() + datetime.timedelta(hours=0.5), datetime.datetime.now() + datetime.timedelta(hours=1))]

def test_calendar_expiration_and_cleanup():
expire_calendars(datetime.datetime.now())

if __name__ == '__main__':
test_oauth_authentication()
test_calendar_creation_and_sharing()
test_availability_windows_input_and_storage()
test_availability_intersection_algorithm()
test_calendar_expiration_and_cleanup()