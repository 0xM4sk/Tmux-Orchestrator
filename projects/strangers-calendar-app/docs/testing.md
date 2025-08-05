|
# Testing Procedures

## Test Plan Summary
- **OAuth Authentication Flows**: Phone number registration, Google, Apple OAuth.
- **Phone Number and WhatsApp Integration**: Register phone numbers via WhatsApp.
- **Calendar Creation and Sharing**: Create a calendar for a user.
- **Availability Windows Input and Storage**: Add availability windows for a user.
- **Availability Intersection Algorithm**: Find intersection of availability windows between two users.
- **Calendar Expiration and Cleanup**: Clean up expired calendars.

## Test Suites
- `tests/test_oauth.py`
- `tests/test_phone_registration.py`
- `tests/test_calendar_creation.py`
- `tests/test_availability_addition.py`
- `tests/test_availability_intersection.py`
- `tests/test_cleanup_calendars.py`

## Maintenance
- Update test suites as new features are added.
- Ensure all tests pass before approving any changes.