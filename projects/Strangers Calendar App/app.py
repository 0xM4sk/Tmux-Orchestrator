|
from flask import Flask, Blueprint
from backend.auth.register import register_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///strangers_calendar.db'
db.init_app(app)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_bp.add_url_rule('/register', view_func=register_user, methods=['POST'])

app.register_blueprint(auth_bp)