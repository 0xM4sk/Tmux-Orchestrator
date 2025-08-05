|
class CalendarManager:
def __init__(self):
self.calendars = {}

def create_calendar(self, user_id, calendar_details):
if user_id not in self.calendars:
self.calendars[user_id] = []
self.calendars[user_id].append(calendar_details)
return f"Calendar created for {user_id}"

def share_calendar(self, user_id, calendar_id, shared_user_id):
if user_id in self.calendars and calendar_id < len(self.calendars[user_id]):
calendar = self.calendars[user_id][calendar_id]
if shared_user_id not in self.calendars:
self.calendars[shared_user_id] = []
self.calendars[shared_user_id].append(calendar)
return f"Calendar shared to {shared_user_id}"
else:
return "User or calendar does not exist"