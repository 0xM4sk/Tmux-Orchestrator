|
from flask import Flask
from models.user import db

app = Flask(__name__)

@app.before_first_request
def create_tables():
with app.app_context():
db.create_all()