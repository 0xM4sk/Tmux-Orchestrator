|
from datetime import datetime, timedelta

def create_temporary_calendar():
"""Create a temporary calendar entry."""
start_time = datetime.now()
end_time = start_time + timedelta(hours=1)
return {
'start_time': start_time,
'end_time': end_time,
'title': 'Temporary Event'
}