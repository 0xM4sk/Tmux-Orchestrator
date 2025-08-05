|
# OAuth authentication implementation
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/auth/google')
def google_login():
auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
return redirect(auth_url)

@app.route('/auth/apple')
def apple_login():
auth_url = 'https://appleid.apple.com/auth/authorize'
return redirect(auth_url)