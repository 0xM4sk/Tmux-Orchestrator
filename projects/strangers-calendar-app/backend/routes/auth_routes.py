|
from flask import Flask, request, jsonify
from .auth.handle_google_auth import google_login, google_logout
from .auth.handle_apple_auth import apple_login, apple_logout

app = Flask(__name__)

@app.route('/login/google', methods=['GET'])
def login_google():
return google_login()

@app.route('/logout/google', methods=['GET'])
def logout_google():
return google_logout()

@app.route('/login/apple', methods=['GET'])
def login_apple():
return apple_login()

@app.route('/logout/apple', methods=['GET'])
def logout_apple():
return apple_logout()