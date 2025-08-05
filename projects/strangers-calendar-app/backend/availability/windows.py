|
# Availability window logic implementation
from datetime import datetime, timedelta

def parse_availability_window(window_str):
start_time = datetime.strptime(window_str.split('-')[0], '%Y-%m-%d %H:%M')
end_time = datetime.strptime(window_str.split('-')[1], '%Y-%m-%d %H:%M')
return {'start': start_time, 'end': end_time}

def is_window_valid(window):
return window['start'] < window['end']

def save_availability_window(window_data):
# Placeholder for saving logic
print(f"Saving availability window: {window_data}")