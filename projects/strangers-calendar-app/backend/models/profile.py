|
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Profile(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
bio = db.Column(db.String(500), default='')
profile_picture_url = db.Column(db.String(255), default='https://via.placeholder.com/150')

def __repr__(self):
return f'<Profile {self.user_id}>'