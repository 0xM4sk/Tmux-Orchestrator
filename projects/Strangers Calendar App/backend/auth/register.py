|
from flask import request, jsonify
from .auth_utils import generate_token
from ..models.user import User

def register_user():
data = request.get_json()
username = data.get('username')
password = data.get('password')

if not username or not password:
return jsonify({'error': 'Username and password are required'}), 400

user = User.query.filter_by(username=username).first()

if user:
return jsonify({'error': 'User already exists'}), 409

new_user = User(username=username, password=password)
new_user.save()

token = generate_token(user.id)

return jsonify({
'message': 'User registered successfully',
'token': token
}), 201