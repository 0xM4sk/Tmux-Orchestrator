|
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/google')
def google_auth():
return redirect(get_google_auth_url())

@auth_bp.route('/apple')
def apple_auth():
return redirect(get_apple_auth_url())