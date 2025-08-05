|
from datetime import datetime, timedelta

class AvailabilityStorage:
def __init__(self):
self.availability_windows = []

def add_availability(self, user_id, start_time, end_time):
if not (start_time < end_time and isinstance(start_time, datetime) and isinstance(end_time, datetime)):
raise ValueError("Invalid start or end time")
self.availability_windows.append((user_id, start_time, end_time))

def update_availability(self, user_id, new_start_time, new_end_time):
if not (new_start_time < new_end_time and isinstance(new_start_time, datetime) and isinstance(new_end_time, datetime)):
raise ValueError("Invalid start or end time")
for i, (uid, start, end) in enumerate(self.availability_windows):
if uid == user_id:
self.availability_windows[i] = (user_id, new_start_time, new_end_time)
return
raise KeyError("User ID not found")

def delete_availability(self, user_id):
for i, (uid, _, _) in enumerate(self.availability_windows):
if uid == user_id:
del self.availability_windows[i]
return
raise KeyError("User ID not found")

def get_availability(self, user_id):
for uid, start, end in self.availability_windows:
if uid == user_id:
return start, end
return None, None