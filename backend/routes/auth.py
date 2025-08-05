|
# Authentication routes
from flask import Flask, redirect, url_for, session
from .auth.google import google
from .auth.apple import apple

@app.route('/login/google')
def login_google():
redirect_uri = url_for('authorize', provider='google', _external=True)
return google.authorize_redirect(redirect_uri)

@app.route('/login/apple')
def login_apple():
redirect_uri = url_for('authorize', provider='apple', _external=True)
return apple.authorize_redirect(redirect_uri)

@app.route('/authorize/<provider>')
def authorize(provider):
if provider == 'google':
token = google.authorize_access_token()
resp = google.get('userinfo')
user_info = resp.json()
# Handle Google authentication
session['user'] = user_info
return redirect(url_for('home'))
elif provider == 'apple':
token = apple.authorize_access_token()
resp = apple.get('userinfo')
user_info = resp.json()
# Handle Apple authentication
session['user'] = user_info
return redirect(url_for('home'))