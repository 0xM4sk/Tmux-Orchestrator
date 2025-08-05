|
from flask_sqlalchemy import SQLAlchemy
from .models.user import User

db = SQLAlchemy()

def init_db():
db.create_all()