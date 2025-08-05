|
# Mock calendar implementation
def create_calendar(user_id):
print(f"Creating calendar for user {user_id}")
return f"Calendar-{user_id}"

def share_calendar(calendar_id, recipient_id):
print(f"Sharing calendar {calendar_id} with user {recipient_id}")