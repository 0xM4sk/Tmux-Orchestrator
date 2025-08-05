|
from .models.user import User, db

def register_user(username, password):
user = User.query.filter_by(username=username).first()
if user:
raise ValueError('Username already exists')

new_user = User(username=username, password=password)
db.session.add(new_user)
db.session.commit()
return new_user