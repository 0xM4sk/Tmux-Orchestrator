|
# OAuth authentication implementation
from flask import Flask, request, redirect, jsonify
from .google_auth import google_oauth_callback
from .apple_auth import apple_oauth_callback

app = Flask(__name__)

@app.route('/auth/google', methods=['GET'])
def google_oauth():
return redirect('https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5000/auth/google/callback&response_type=code&scope=email')

@app.route('/auth/google/callback', methods=['GET'])
def google_oauth_callback():
code = request.args.get('code')
return google_oauth_callback(code)

@app.route('/auth/apple', methods=['GET'])
def apple_oauth():
return redirect('https://appleid.apple.com/auth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5000/auth/apple/callback&scope=email')

@app.route('/auth/apple/callback', methods=['GET'])
def apple_oauth_callback():
code = request.args.get('code')
return apple_oauth_callback(code)

if __name__ == '__main__':
app.run(debug=True)