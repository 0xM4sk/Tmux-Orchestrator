|
# OAuth endpoints for Google and Apple
from flask import Flask, request, redirect
from .oauth import google_auth, apple_auth

app = Flask(__name__)

@app.route('/google/login')
def login_google():
return google_auth()

@app.route('/apple/login')
def login_apple():
return apple_auth()