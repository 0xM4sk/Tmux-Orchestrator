|
from flask import request, jsonify
from functools import wraps
from .models.user import User

def token_required(f):
@wraps(f)
def decorator(*args, **kwargs):
token = request.args.get('token')

if not token:
return jsonify({'message': 'Token is missing!'}), 403

return f(*args, **kwargs)

return decorator

@app.route('/user', methods=['POST'])
def create_user():
data = request.get_json()
new_user = User(username=data['username'], email=data['email'], password_hash=data['password_hash'])
db.session.add(new_user)
db.session.commit()
return jsonify({'message': 'New user created!'}), 201

@app.route('/user', methods=['GET'])
@token_required
def get_user():
token = request.args.get('token')
# Assume we have a function to decode the token and get the current user
current_user = decode_token(token)
return jsonify({'username': current_user.username, 'email': current_user.email}), 200

@app.route('/user', methods=['PUT'])
@token_required
def update_user():
data = request.get_json()
token = request.args.get('token')
# Assume we have a function to decode the token and get the current user
current_user = decode_token(token)
current_user.username = data['username']
current_user.email = data['email']
db.session.commit()
return jsonify({'message': 'User updated!'}), 200

@app.route('/user', methods=['DELETE'])
@token_required
def delete_user():
token = request.args.get('token')
# Assume we have a function to decode the token and get the current user
current_user = decode_token(token)
db.session.delete(current_user)
db.session.commit()
return jsonify({'message': 'User deleted!'}), 200