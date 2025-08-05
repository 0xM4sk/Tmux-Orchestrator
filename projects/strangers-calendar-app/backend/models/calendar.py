|
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TemporaryCalendar(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, nullable=False)
start_time = db.Column(db.DateTime, nullable=False)
end_time = db.Column(db.DateTime, nullable=False)
created_at = db.Column(db.DateTime, default=datetime.utcnow)

def is_expired(self):
return self.created_at + timedelta(days=1) < datetime.utcnow()