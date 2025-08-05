|
# Callback handlers for Google and Apple
from flask import Flask, request, redirect, url_for
from .oauth import google_callback, apple_callback

app = Flask(__name__)

@app.route('/google/callback')
def google_callback():
return google_callback()

@app.route('/apple/callback')
def apple_callback():
return apple_callback()