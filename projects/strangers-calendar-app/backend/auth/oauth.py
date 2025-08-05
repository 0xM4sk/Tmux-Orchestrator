|
# OAuth authentication implementation
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/auth/google')
def google_auth():
return redirect('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri=http%3A//localhost:5000/callback/google')

@app.route('/callback/google')
def google_callback():
code = request.args.get('code')
# Exchange the authorization code for an access token
return f"Code received: {code}"

@app.route('/auth/apple')
def apple_auth():
return redirect('https://appleid.apple.com/auth/authorize?response_type=code&client_id=YOUR_APPLE_CLIENT_ID&redirect_uri=http%3A//localhost:5000/callback/apple')

@app.route('/callback/apple')
def apple_callback():
code = request.args.get('code')
# Exchange the authorization code for an access token
return f"Code received: {code}"