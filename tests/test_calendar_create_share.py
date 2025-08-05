|
import pytest
from backend.calendar.create_share import create_calendar, share_calendar, get_shared_calendars

def test_create_calendar():
calendar = create_calendar(1, "My Calendar")
assert calendar["user_id"] == 1
assert calendar["calendar_name"] == "My Calendar"
assert "created_at" in calendar

def test_share_calendar():
calendar = create_calendar(1, "My Calendar")
share_calendar(calendar["calendar_name"], [2, 3])
# Add assertions to verify sharing logic

def test_get_shared_calendars():
shared_calendars = get_shared_calendars(1)
assert isinstance(shared_calendars, list)

# Run the tests
pytest