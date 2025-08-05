|
from .models import TemporaryCalendar
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_calendar(user_id, start_time, end_time):
calendar = TemporaryCalendar(user_id=user_id, start_time=start_time, end_time=end_time)
db.session.add(calendar)
db.session.commit()
return calendar

def get_calendar_by_id(calendar_id):
return TemporaryCalendar.query.get(calendar_id)

def share_calendar(calendar_id, recipient_phone_number):
calendar = get_calendar_by_id(calendar_id)
if not calendar:
raise ValueError("Calendar not found")

message = f"Check out my calendar: {calendar.start_time} to {calendar.end_time}"
send_whatsapp_message(recipient_phone_number, message)