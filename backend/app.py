|
from flask import Flask
from backend.auth.oauth import app as auth_app
from backend.calendars.availability import app as calendar_app

app = Flask(__name__)

app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(calendar_app, url_prefix='/calendars')

if __name__ == '__main__':
app.run(debug=True)