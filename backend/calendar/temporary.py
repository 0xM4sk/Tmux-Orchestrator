|
from datetime import datetime, timedelta

def create_temporary_calendar(user_id):
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)
event = {
'user_id': user_id,
'start_time': start_time.isoformat(),
'end_time': end_time.isoformat(),
'title': 'Temporary Calendar Entry',
'is_temporary': True
}
# Save the event to your database
return event