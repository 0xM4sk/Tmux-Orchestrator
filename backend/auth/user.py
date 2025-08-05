|
from flask import Flask, request, jsonify
from .oauth import authenticate_user

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login_user():
data = request.get_json()
username = data.get('username')
password = data.get('password')

# Check if OAuth authentication is preferred
oauth_token = data.get('oauth_token')
if oauth_token:
user = authenticate_user(oauth_token)
if user:
return jsonify({'message': 'Login successful'}), 200

return jsonify({'message': 'Invalid credentials'}), 400